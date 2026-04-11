import streamlit as st


def add_disclaimer():
    """
    Tampilkan disclaimer di footer
    """
    st.markdown("---")
    st.warning("""
    > ⚠️ **DISCLAIMER**: 
    > 
    > Semua informasi dalam aplikasi ini adalah untuk tujuan **edukasi dan informasi saja**. 
    > Trading forex dan instrumen finansial lainnya memiliki **risiko tinggi** dan dapat mengakibatkan kehilangan modal.
    > 
    > - Kinerja masa lalu tidak menjamin hasil masa depan
    > - Selalu lakukan riset mandiri (DYOR - Do Your Own Research)
    > - Gunakan risk management yang ketat (max 1-2% risk per trade)
    > - Konsultasikan dengan penasihat keuangan profesional sebelum trading
    > - Pengembang aplikasi tidak bertanggung jawab atas kerugian yang mungkin timbul
    > 
    > **Trade responsibly!** 📊
    """)