# ==========================================================================
# PHAN MEM DIEU DO CONG VIEC - BAN DEPLOY LEN HUGGING FACE SPACES
# Thuat toan: FCFS, SPT, LPT, EDD, SRPT
# File nay dat ten la "app.py" khi upload len Hugging Face Space.
# ==========================================================================

import gradio as gr
import pandas as pd
import matplotlib.pyplot as plt


# =====================================================================
# CAC THUAT TOAN DIEU DO  <-- QUAN TRONG (LA TOAN HOC)
# =====================================================================
def fcfs(danh_sach):
    return danh_sach.copy()

def spt(danh_sach):
    return sorted(danh_sach, key=lambda job: job["p"])

def lpt(danh_sach):
    return sorted(danh_sach, key=lambda job: -job["p"])

def edd(danh_sach):
    return sorted(danh_sach, key=lambda job: job["d"])

def srpt(danh_sach):
    return spt(danh_sach)

DANH_SACH_THUAT_TOAN = {"FCFS": fcfs, "SPT": spt, "LPT": lpt, "EDD": edd, "SRPT": srpt}


# CONG THUC TINH KET QUA  <-- QUAN TRONG NHAT
#   C_i = C_(i-1) + P_i      thoi diem hoan thanh
#   L_i = C_i - D_i          do tre
#   T_i = max(0, L_i)        do tre duong
def tinh_ket_qua(thu_tu_da_sap_xep):
    ket_qua = []
    C = 0
    for job in thu_tu_da_sap_xep:
        bat_dau = C
        C = bat_dau + job["p"]
        L = C - job["d"]
        T = max(0, L)
        ket_qua.append({"ten": job["ten"], "bat_dau": bat_dau, "p": job["p"],
                         "hoan_thanh": C, "d": job["d"], "tre": L, "tre_duong": T})
    return ket_qua


# =====================================================================
# HAM XU LY CHINH (doc bang -> chay thuat toan -> tra ve ket qua)
# =====================================================================
def xu_ly(bang_nhap, ten_thuat_toan):
    danh_sach = []
    for _, dong in bang_nhap.iterrows():
        p = dong["Pi"]
        d = dong["Di"]
        if p is None or p == "" or float(p) <= 0:
            continue
        if d is None or d == "":
            d = 0
        danh_sach.append({"ten": str(dong["Cong viec"]), "p": float(p), "d": float(d)})

    if len(danh_sach) == 0:
        return None, pd.DataFrame(), "Chua co du lieu hop le. Vui long nhap Pi > 0."

    thu_tu = DANH_SACH_THUAT_TOAN[ten_thuat_toan](danh_sach)
    ket_qua = tinh_ket_qua(thu_tu)

    fig, ax = plt.subplots(figsize=(8, 1.2 + 0.4 * len(ket_qua)))
    mau_sac = plt.cm.tab20.colors
    for i, r in enumerate(ket_qua):
        ax.barh(0, r["p"], left=r["bat_dau"], color=mau_sac[i % len(mau_sac)], edgecolor="black")
        ax.text(r["bat_dau"] + r["p"] / 2, 0, r["ten"], ha="center", va="center",
                color="white", fontweight="bold")
    ax.set_yticks([])
    ax.set_xlabel("Thoi gian")
    ax.set_title(f"So do Gantt - {ten_thuat_toan}")
    plt.tight_layout()

    df_ket_qua = pd.DataFrame([{
        "Cong viec": r["ten"], "Bat dau": r["bat_dau"], "Pi": r["p"],
        "Hoan thanh (Ci)": r["hoan_thanh"], "Di": r["d"],
        "Tre (Li)": r["tre"], "Tre duong (Ti)": r["tre_duong"],
    } for r in ket_qua])

    n = len(ket_qua)
    Cmax = ket_qua[-1]["hoan_thanh"]
    tong_T = sum(r["tre_duong"] for r in ket_qua)
    so_job_tre = sum(1 for r in ket_qua if r["tre_duong"] > 0)
    tong_hop = (f"Cmax (Makespan) = {Cmax:.2f}\n"
                f"So cong viec bi tre han = {so_job_tre}/{n}\n"
                f"Tong do tre duong (Tong Ti) = {tong_T:.2f}")

    return fig, df_ket_qua, tong_hop


# =====================================================================
# GIAO DIEN GRADIO
# =====================================================================
bang_mau = pd.DataFrame({
    "Cong viec": [f"J{i}" for i in range(1, 11)],
    "Pi": [0] * 10,
    "Di": [0] * 10,
})

with gr.Blocks(title="Phan mem dieu do cong viec") as app:
    gr.Markdown("## Phan mem giai thuat toan dieu do (FCFS / SPT / LPT / EDD / SRPT)")
    gr.Markdown("Nhap Pi, Di truc tiep vao bang duoi. Dong nao chua dung thi de Pi = 0.")

    bang_nhap = gr.Dataframe(value=bang_mau, headers=["Cong viec", "Pi", "Di"],
                              datatype=["str", "number", "number"], row_count=10, col_count=3)

    chon_thuat_toan = gr.Dropdown(choices=list(DANH_SACH_THUAT_TOAN.keys()),
                                   value="SPT", label="Chon giai thuat")

    nut_chay = gr.Button("Chay dieu do", variant="primary")

    bieu_do_gantt = gr.Plot(label="So do Gantt")
    bang_ket_qua = gr.Dataframe(label="Bang ket qua")
    o_tong_hop = gr.Textbox(label="Chi so tong hop", lines=4)

    nut_chay.click(fn=xu_ly, inputs=[bang_nhap, chon_thuat_toan],
                    outputs=[bieu_do_gantt, bang_ket_qua, o_tong_hop])

# KHONG dung share=True o day - Hugging Face Space tu cap link vinh vien
app.launch()
