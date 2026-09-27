import hashlib
from datetime import datetime, timezone
from io import BytesIO

import qrcode
import streamlit as st

st.set_page_config(page_title="DPP-Gate | ESPR Compliance Engine", layout="wide")

st.title("🛡️ DPP-Gate: Ecodesign Techno-Regulatory Gateway")
st.caption(
    "Architectural Enforcement of ESPR (Ecodesign for Sustainable Products Regulation)"
)

# Sidebar: Regulatory Thresholds (Code as Law)
st.sidebar.header("⚖️ ESPR Delegated Act Criteria")
MIN_RECYCLED_CONTENT = st.sidebar.slider("Min Recycled Plastic (%)", 0, 100, 30)
MIN_REPAIRABILITY = st.sidebar.slider("Min Repairability Index (0-10)", 0.0, 10.0, 6.5)

# Form Input
with st.form("dpp_submission"):
    st.subheader("1. Entity & Product Identifiers (DIDs)")
    col1, col2, col3 = st.columns(3)
    upi = col1.text_input(
        "Unique Product Identifier (UPI)", "did:web:brand.eu:products:sku-992"
    )
    uoi = col2.text_input("Unique Operator Identifier (UOI)", "did:web:brand.eu")
    ufi = col3.text_input(
        "Unique Facility Identifier (UFI)", "did:web:supplier.com:plant-4"
    )

    st.subheader("2. Circularity & Environmental Metrics")
    m1, m2, m3 = st.columns(3)
    recycled_pct = m1.number_input(
        "Post-Consumer Recycled Content (%)", min_value=0, max_value=100, value=35
    )
    repair_score = m2.number_input(
        "Repairability Index", min_value=0.0, max_value=10.0, value=7.2, step=0.1
    )
    has_svhc = m3.selectbox(
        "Contains Substances of Very High Concern (SVHC > 0.1%)?", ["No", "Yes"]
    )

    submitted = st.form_submit_button("Evaluate Market Conformity")

if submitted:
    st.divider()

    # Techno-legal constraint check (Architectural Enforcement)
    failures = []
    if recycled_pct < MIN_RECYCLED_CONTENT:
        failures.append(
            f"Recycled content ({recycled_pct}%) fails statutory threshold ({MIN_RECYCLED_CONTENT}%)."
        )
    if repair_score < MIN_REPAIRABILITY:
        failures.append(
            f"Repairability index ({repair_score}) fails statutory threshold ({MIN_REPAIRABILITY})."
        )
    if has_svhc == "Yes":
        failures.append(
            "Undisclosed/Unpermitted SVHC present above regulatory reporting limit."
        )
    if not (
        upi.startswith("did:") and uoi.startswith("did:") and ufi.startswith("did:")
    ):
        failures.append("Identifiers do not conform to standardized DID URI syntax.")

    # 1. Failure Case: Techno-regulation blocks market entry
    if failures:
        st.error("🚫 MARKET ENTRY BLOCKED: Product Non-Compliant with ESPR")
        for f in failures:
            st.write(f"- {f}")
        st.warning(
            "Techno-Regulatory Action: DPP minting denied. Public QR code generation suppressed."
        )

    # 2. Success Case: Verifiable Credential issued + QR minted
    else:
        st.success("✅ CONFORMITY VERIFIED: Product Meets ESPR Ecodesign Criteria")

        # Mint W3C Verifiable Credential payload
        vc_payload = {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://w3id.org/dpp/v1",
            ],
            "type": ["VerifiableCredential", "DigitalProductPassport"],
            "issuer": uoi,
            "issuanceDate": datetime.now(timezone.utc).isoformat(),
            "credentialSubject": {
                "id": upi,
                "facility": ufi,
                "circularity": {
                    "recycledContentPercentage": recycled_pct,
                    "repairabilityIndex": repair_score,
                    "svhcDeclared": False,
                },
            },
            "proof": {
                "type": "Ed25519Signature2020",
                "created": datetime.now(timezone.utc).isoformat(),
                "verificationMethod": f"{uoi}#key-1",
                "proofValue": hashlib.sha256(
                    f"{upi}{recycled_pct}".encode()
                ).hexdigest(),
            },
        }

        col_left, col_right = st.columns([3, 2])
        with col_left:
            st.subheader("W3C Verifiable Credential (VC)")
            st.json(vc_payload)

        with col_right:
            st.subheader("Consumer Product Passport (QR)")
            target_url = f"https://dpp.resolver.eu/{upi}"

            # Generate actual QR code
            qr = qrcode.QRCode(box_size=8, border=2)
            qr.add_data(target_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            buf = BytesIO()
            img.save(buf, format="PNG")
            st.image(buf.getvalue(), caption=f"ESPR Compliant Carrier: {upi}")
            st.info(f"Resolves to: `{target_url}`")
