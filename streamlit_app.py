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
st.title("😂 카톤 라벨 자동 생성기👌👌")

k_font = load_korean_font()

# =========================================================================
# [기존 기능] 1. 엑셀 파일 업로드 라벨 생성기 (순정 로직 그대로 유지)
# =========================================================================
st.write("### 📁 엑셀파일 업로드 자동 생성")
uploaded_file = st.file_uploader("Upload Excel File (.xlsx)", type=['xlsx'], key="live_excel_uploader")

if uploaded_file:
    uploaded_file.seek(0)
    df = pd.read_excel(uploaded_file)
    st.write("### 1. 미리보기 / 데이터 점검")
    st.dataframe(df.head())

    if st.button("🚀 Generate 100x80mm PDF (Excel)", use_container_width=True):
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
            label="📥 Download Excel PDF",
            data=buffer.getvalue(),
            file_name=final_filename,
            mime="application/pdf",
            use_container_width=True
        )

# 중간 시각 구분선
st.write("---")

# =========================================================================
# [신규 기능] 2. 라벨 수동 생성 (항목 직접 입력 모듈)
# =========================================================================
st.write("### 😇 손으로 써서 라벨 수동 생성👇👇 ")

manual_1 = st.text_input("📦 1번째 칸 (품목코드 등)", placeholder="예: 12345A", key="m_1")
manual_2 = st.text_input("📝 2번째 칸 (영문 품명)", placeholder="예: SAPEIO SUGAR BODY SCRUB 500g ", key="m_2")
manual_3 = st.text_input("🔢 3번째 칸 (한글 품명/#bag)", placeholder="예: 슈가 바디 스크럽 500g / #01", key="m_3")
manual_4 = st.text_input("⚖️ 4번째 칸 (#PO)", placeholder="예: PO#1106101022 or -", key="m_4")
manual_5 = st.text_input("🏭 5번째 칸 (개입수)", placeholder="예: 30EA", key="m_5")

# [수정] 대표님이 끊기셨던 number_input 마감 처리 완공
manual_count = st.number_input("🔢 생성할 라벨 장수", min_value=1, value=1, step=1, key="m_count")

if st.button("🚀 Generate 100x80mm PDF (수동)", use_container_width=True):
    if not manual_1:
        st.error("❌ 최소 1번째 칸(품목코드) 데이터는 입력해야 라벨 생성이 가능합니다.")
    else:
        manual_buffer = BytesIO()
        manual_c = canvas.Canvas(manual_buffer, pagesize=(4*inch, 3*inch))
        
        for _ in range(int(manual_count)):
            margin = 0.1 * inch
            manual_c.setLineWidth(2)
            manual_c.rect(margin, margin, 4*inch - (2*margin), 3*inch - (2*margin))
            
            inner_h = 3*inch - (2*margin)
            h_unit = inner_h / 5
            
            manual_data = [manual_1, manual_2, manual_3, manual_4, manual_5]
            
            for i in range(5):
                y_top = (3*inch - margin) - (i * h_unit)
                manual_c.setLineWidth(1)
                if i > 0:
                    manual_c.line(margin, y_top, 4*inch - margin, y_top)
                
                val = manual_data[i].strip() if manual_data[i] else ""
                
                if i == 0:
                    manual_c.setFont(k_font, 28)
                    manual_c.drawString(margin + 0.15*inch, y_top - 0.45*inch, val)
                elif i == 1:
                    manual_c.setFont(k_font, 18)
                    lines = textwrap.wrap(val, width=22)
                    if len(lines) > 1:
                        manual_c.drawString(margin + 0.15*inch, y_top - 0.25*inch, lines[0])
                        manual_c.drawString(margin + 0.15*inch, y_top - 0.52*inch, lines[1])
                    else:
                        manual_c.drawString(margin + 0.15*inch, y_top - 0.4*inch, val)
                elif i == 2:
                    text_len = len(val)
                    font_size = 14 if text_len > 18 else (18 if text_len > 14 else 22)
                    manual_c.setFont(k_font, font_size)
                    manual_c.drawString(margin + 0.15*inch, y_top - 0.42*inch, val)
                else:
                    manual_c.setFont(k_font, 22)
                    manual_c.drawString(margin + 0.15*inch, y_top - 0.42*inch, val)
            
            manual_c.showPage()
        
        manual_c.save()
        
        manual_filename = f"{manual_1.strip()}_manual_label.pdf"
        st.success(f"Success! Manual File: {manual_filename}")
        st.download_button(
            label="📥 Download Manual PDF",
            data=manual_buffer.getvalue(),
            file_name=manual_filename,
            mime="application/pdf",
            use_container_width=True
        )