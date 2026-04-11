import streamlit as st
import pandas as pd
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="⭐ Watchlist", layout="wide")

# Initialize watchlist in session state
if "watchlist" not in st.session_state:
    st.session_state.watchlist = ["EUR/USD", "GBP/USD", "USD/JPY"]

def main():
    st.title("⭐ Watchlist")
    
    # Add pair section
    c1, c2 = st.columns([3, 1])
    
    with c1:
        new_pair = st.selectbox(
            "Add Pair",
            ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD", "NZD/USD", "EUR/GBP"]
        )
    
    with c2:
        if st.button("➕ Add to Watchlist"):
            if new_pair not in st.session_state.watchlist:
                st.session_state.watchlist.append(new_pair)
                st.success(f"✅ {new_pair} added to watchlist!")
                st.rerun()
            else:
                st.warning(f"⚠️ {new_pair} already in watchlist")
    
    st.markdown("---")
    
    # Display watchlist
    if st.session_state.watchlist:
        st.markdown(f"**Current Watchlist ({len(st.session_state.watchlist)} pairs):**")
        
        watchlist_tags = " | ".join([f"📊 {pair}" for pair in st.session_state.watchlist])
        st.markdown(watchlist_tags)
        
        st.markdown("---")
        
        # Create data table
        data = []
        for pair in st.session_state.watchlist:
            data.append({
                "Pair": pair,
                "Status": "🟢 Monitoring",
                "Last Check": datetime.now().strftime("%H:%M:%S"),
                "Alert": "None"
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Remove option
        st.markdown("---")
        remove_pair = st.selectbox("Remove Pair", st.session_state.watchlist)
        
        if st.button("🗑️ Remove Selected"):
            if remove_pair in st.session_state.watchlist:
                st.session_state.watchlist.remove(remove_pair)
                st.success(f"✅ {remove_pair} removed from watchlist!")
                st.rerun()
        
        # Clear all
        if st.button("🗑️ Clear All Watchlist"):
            st.session_state.watchlist = []
            st.success("✅ Watchlist cleared!")
            st.rerun()
    
    else:
        st.info("📭 Watchlist kosong. Tambahkan pair untuk memulai monitoring.")
    
    st.caption("💡 Watchlist tersimpan selama sesi browser aktif")

if __name__ == "__main__":
    main()