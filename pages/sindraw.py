import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="What is Most Similar", layout="wide")
st.title("🎨 What is Most Similar: Draw the Sine Function!")

st.markdown("좌표평면 위에 사인 함수를 그려보세요.")

# ============================================================================
# SETTINGS
# ============================================================================
st.sidebar.header("⚙️ Canvas Settings")
canvas_width = st.sidebar.slider("Canvas Width", 500, 800, 700)
canvas_height = st.sidebar.slider("Canvas Height", 300, 500, 400)
stroke_width = st.sidebar.slider("Stroke Width", 1, 20, 3)

# ============================================================================
# CREATE COORDINATE PLANE WITH HTML/CSS/SVG
# ============================================================================
def create_coordinate_grid_svg(width, height):
    """좌표평면을 SVG로 생성합니다. X축(0~2π), Y축(-1~1)"""
    # 여백 설정
    padding = 40
    plot_width = width - 2 * padding
    plot_height = height - 2 * padding
    
    # 격자선 개수
    grid_x_count = 16  # 약 π/2 단위
    grid_y_count = 8   # 0.25 단위
    
    svg_lines = [f'<svg width="{width}" height="{height}" style="background-color: white; border: 1px solid #ccc;">']
    
    # 격자선 (세로)
    for i in range(grid_x_count + 1):
        x = padding + (i / grid_x_count) * plot_width
        svg_lines.append(
            f'<line x1="{x}" y1="{padding}" x2="{x}" y2="{height - padding}" '
            f'stroke="lightgray" stroke-width="0.5" opacity="0.5"/>'
        )
    
    # 격자선 (가로)
    for i in range(grid_y_count + 1):
        y = padding + (i / grid_y_count) * plot_height
        svg_lines.append(
            f'<line x1="{padding}" y1="{y}" x2="{width - padding}" y2="{y}" '
            f'stroke="lightgray" stroke-width="0.5" opacity="0.5"/>'
        )
    
    # X축 (중앙 수평선)
    y_axis_pos = padding + (plot_height / 2)
    svg_lines.append(
        f'<line x1="{padding}" y1="{y_axis_pos}" x2="{width - padding}" y2="{y_axis_pos}" '
        f'stroke="black" stroke-width="2"/>'
    )
    
    # Y축 (중앙 수직선)
    x_axis_pos = padding + (plot_width / 2)
    svg_lines.append(
        f'<line x1="{x_axis_pos}" y1="{padding}" x2="{x_axis_pos}" y2="{height - padding}" '
        f'stroke="black" stroke-width="2"/>'
    )
    
    # X축 눈금 및 라벨 (0, π/2, π, 3π/2, 2π)
    special_angles = [0, np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi]
    angle_labels = ['0', 'π/2', 'π', '3π/2', '2π']
    
    for angle, label in zip(special_angles, angle_labels):
        x_pos = padding + (angle / (2 * np.pi)) * plot_width
        # 눈금선
        svg_lines.append(
            f'<line x1="{x_pos}" y1="{y_axis_pos - 8}" x2="{x_pos}" y2="{y_axis_pos + 8}" '
            f'stroke="black" stroke-width="1.5"/>'
        )
        # 라벨
        svg_lines.append(
            f'<text x="{x_pos}" y="{y_axis_pos + 25}" text-anchor="middle" font-size="11" font-weight="bold">'
            f'{label}</text>'
        )
    
    # Y축 눈금 및 라벨 (-1, 0, 1)
    y_labels = [(-1, '-1'), (0, '0'), (1, '1')]
    
    for y_val, y_label in y_labels:
        y_pos = padding + (0.5 - y_val / 2) * plot_height  # y_val 범위: -1 ~ 1
        # 눈금선
        svg_lines.append(
            f'<line x1="{x_axis_pos - 8}" y1="{y_pos}" x2="{x_axis_pos + 8}" y2="{y_pos}" '
            f'stroke="black" stroke-width="1.5"/>'
        )
        # 라벨
        svg_lines.append(
            f'<text x="{x_axis_pos - 20}" y="{y_pos + 4}" text-anchor="end" font-size="11" font-weight="bold">'
            f'{y_label}</text>'
        )
    
    svg_lines.append('</svg>')
    return '\n'.join(svg_lines)

# ============================================================================
# DISPLAY CANVAS WITH OVERLAY
# ============================================================================
st.subheader("✏️ Draw the Sine Function")

# HTML 컨테이너 생성
grid_svg = create_coordinate_grid_svg(canvas_width, canvas_height)

# 배경 좌표평면과 캔버스를 겹겹이 배치
container_html = f"""
<div style="position: relative; display: inline-block; width: {canvas_width}px; height: {canvas_height}px; margin: 10px 0;">
    <div style="position: absolute; top: 0; left: 0; z-index: 1;">
        {grid_svg}
    </div>
    <div style="position: absolute; top: 0; left: 0; z-index: 2;">
        <!-- st_canvas가 여기에 렌더링됩니다 -->
    </div>
</div>
"""

st.markdown(container_html, unsafe_allow_html=True)

# 투명 배경 캔버스
canvas_result = st_canvas(
    fill_color="rgba(0,0,0,0)",
    stroke_width=stroke_width,
    stroke_color="#000000",
    background_color="rgba(0,0,0,0)",
    height=canvas_height,
    width=canvas_width,
    drawing_mode="freedraw",
    key="canvas_sine"
)

# ============================================================================
# ANALYSIS & SCORING
# ============================================================================
if canvas_result.image_data is not None:
    st.subheader("📊 Analysis Results")

    try:
        img = canvas_result.image_data
        # 검은색 픽셀 추출
        black_pixels = np.where(
            (img[:, :, 0] < 50)
            & (img[:, :, 1] < 50)
            & (img[:, :, 2] < 50)
            & (img[:, :, 3] > 200)
        )

        if len(black_pixels[0]) > 20:
            # 픽셀 좌표 정렬
            coords = np.column_stack((black_pixels[1], black_pixels[0]))
            coords = coords[np.argsort(coords[:, 0])]

            # 중복 제거
            unique_x_indices = np.unique(coords[:, 0], return_index=True)[1]
            coords = coords[unique_x_indices]

            if len(coords) > 10:
                x_pixels = coords[:, 0].astype(float)
                y_pixels = coords[:, 1].astype(float)

                # 캔버스 픽셀 좌표 → 수학 좌표로 변환
                # X축: 0 ~ 2π
                # Y축: 1 (상단) ~ -1 (하단)
                x_math = (x_pixels / canvas_width) * 2 * np.pi
                y_math = 1 - (2 * y_pixels / canvas_height)

                # 유효한 범위 필터링 (-1.5 ~ 1.5)
                valid_mask = (y_math >= -1.5) & (y_math <= 1.5)
                x_math = x_math[valid_mask]
                y_math = y_math[valid_mask]

                if len(x_math) > 10:
                    # 보간
                    x_interp = np.linspace(0, 2 * np.pi, 100)

                    try:
                        f = interp1d(
                            x_math,
                            y_math,
                            kind='linear',
                            bounds_error=False,
                            fill_value='extrapolate',
                        )
                        y_interp = f(x_interp)
                        y_interp = np.clip(y_interp, -1.5, 1.5)

                        # 비교 그래프
                        st.subheader("📈 Comparison")
                        fig, ax = plt.subplots(figsize=(10, 5))

                        x_full = np.linspace(0, 2 * np.pi, 300)
                        y_full = np.sin(x_full)

                        ax.plot(x_full, y_full, 'b-', linewidth=3, label='Actual sin(x)', alpha=0.7)
                        ax.plot(x_interp, y_interp, 'r-', linewidth=2.5, label='Your Drawing', alpha=0.8)
                        ax.scatter(x_math, y_math, color='red', s=20, alpha=0.4)

                        ax.set_xlim(0, 2 * np.pi)
                        ax.set_ylim(-1.5, 1.5)
                        ax.set_xlabel('Angle (radians)', fontsize=12)
                        ax.set_ylabel('sin(θ)', fontsize=12)
                        ax.legend(fontsize=11)
                        ax.grid(True, alpha=0.3)
                        ax.set_xticks([0, np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi])
                        ax.set_xticklabels(['0', 'π/2', 'π', '3π/2', '2π'])

                        st.pyplot(fig)
                        plt.close(fig)

                        # 유사도 계산
                        mse = np.mean((y_interp - np.sin(x_interp)) ** 2)
                        similarity = max(0, 100 * (1 - mse))
                        st.metric("Similarity Score", f"{similarity:.1f}%")

                    except Exception as e:
                        st.error(f"보간 오류: {str(e)}")
                else:
                    st.info("⚠️ 더 많은 점을 그려주세요.")
            else:
                st.info("⚠️ 캔버스에 선을 그려주세요.")
        else:
            st.info("⚠️ 캔버스에 선을 그려주세요.")

    except Exception as e:
        st.error(f"분석 오류: {str(e)}")

