# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import textwrap
from io import BytesIO
import urllib.request
import os

# [강제 진압 1] 글꼴 다운로드 캐시만 남기고, 데이터와 관련된 모든 캐시 데코레이터 완전 제거
@st.cache_resource
def load_korean_font():
    font_url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf"
    font_path = "NanumGothic-Bold.ttf"
    try:
        if not os.path.exists(font_path):
            req = urllib.request.Request(font_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(font_path, 'wb') as out_file:
                out_file.write(response.read())
        pdfmetrics.registerFont(TTFont('NanumGothic-Bold', font_path))
        return 'NanumGothic-Bold'
    except:
        return "Helvetica-Bold"

st.set_page_config(page_title="Label Generator", layout="wide")
st.title("🏷️ 카톤 라벨 생성기")

k_font = load_korean_font()

# [강제 진압 2] 파일 업로더가 바뀔 때마다 하위 연산들이 완벽하게 리셋되도록 셋팅
uploaded_file = st.file_uploader("Upload Excel File (.xlsx)", type=['xlsx'], key="live_excel_uploader")

if uploaded_file:
    # 매번 메모리를 새로 뚫어서 엑셀 파일의 바이너리를 상시 실시간으로 읽음
    uploaded_file.seek(0)
    df = pd.read_excel(uploaded_file)
    
    st.write("### 1. Data Preview (실시간 동기화 완료)")
    st.dataframe(df.head())

    if st.button("🚀 Generate 100x80mm PDF", use_container_width=True):
        buffer = BytesIO()
        width, height = 4*inch, 3*inch
        c = canvas.Canvas(buffer, pagesize=(width, height))
        
        item_codes = []
        
        for _, row in df.iterrows():
            print_count = 1
            if len(df.columns) >= 6:
                count_val = row.iloc[5]
                if pd.notna(count_val):
                    try:
                        print_count = int(float(count_val))
                        if print_count < 1:
                            print_count = 1
                    except (ValueError, TypeError):
                        print_count = 1
            
            for _ in range(print_count):
                margin = 0.1 * inch
                c.setLineWidth(2)
                c.rect(margin, margin, width - (2*margin), height - (2*margin))
                
                inner_h = height - (2*margin)
                h_unit = inner_h / 5
                
                for i in range(5):
                    y_top = (height - margin) - (i * h_unit)
                    c.setLineWidth(1)
                    if i > 0:
                        c.line(margin, y_top, width - margin, y_top)
                    
                    if i < len(df.columns):
                        val = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else ""
                    else:
                        val = ""
                    
                    if i == 0:
                        c.setFont(k_font, 28)
                        c.drawString(margin + 0.15*inch, y_top - 0.45*inch, val)
                        if val and val != "nan": item_codes.append(val)
                    elif i == 1:
                        c.setFont(k_font, 18)
                        lines = textwrap.wrap(val, width=22)
                        if len(lines) > 1:
                            c.drawString(margin + 0.15*inch, y_top - 0.25*inch, lines[0])
                            c.drawString(margin + 0.15*inch, y_top - 0.52*inch, lines[1])
                        else:
                            c.drawString(margin + 0.15*inch, y_top - 0.4*inch, val)
                    elif i == 2:
                        text_len = len(val)
                        font_size = 14 if text_len > 18 else (18 if text_len > 14 else 22)
                        c.setFont(k_font, font_size)
                        c.drawString(margin + 0.15*inch, y_top - 0.42*inch, val)
                    else:
                        c.setFont(k_font, 22)
                        c.drawString(margin + 0.15*inch, y_top - 0.42*inch, val)
                
                c.showPage()
            
        c.save()
        
        unique_codes = list(dict.fromkeys(item_codes))
        final_filename = f"{','.join(unique_codes)}_carton label.pdf"
        
        st.success(f"Success! File: {final_filename}")
        st.download_button(
            label="📥 Download Final PDF",
            data=buffer.getvalue(),
            file_name=final_filename,
            mime="application/pdf",
            use_container_width=True
        )