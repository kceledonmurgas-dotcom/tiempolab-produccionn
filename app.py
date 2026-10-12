import streamlit as st
import pandas as pd

st.set_page_config(page_title="TiempoLab | Producción", page_icon="⚙️", layout="wide")
st.markdown("""
<style>
.stApp {background:linear-gradient(135deg,#fbf8ff,#fff7fb 55%,#f4f0ff)}
.block-container {max-width:1250px;padding-top:2rem}
h1,h2,h3 {color:#392463}
div[data-testid="stMetric"] {background:#fff;border:1px solid #e4dcf5;padding:16px;border-radius:16px}
div.stButton>button {border-radius:12px;border:0;background:linear-gradient(100deg,#7850ad,#a65b9d);color:white;font-weight:700}
div[data-testid="stVerticalBlockBorderWrapper"] {background:#ffffffc9;border-radius:16px}
</style>
""", unsafe_allow_html=True)

st.title("⚙️ TiempoLab")
st.subheader("Análisis inteligente de tiempos de producción")
st.caption("Herramienta académica de Ingeniería Industrial · Taller de confección")
st.divider()

if "results" not in st.session_state:
    st.session_state.results = None

with st.sidebar:
    st.header("📋 Datos del lote")
    n = st.number_input("Cantidad de productos", min_value=1, max_value=50, value=3, step=1)
    st.caption("Puedes analizar de 1 a 50 productos.")
    demo = st.button("✨ Cargar ejemplo", use_container_width=True)
    if st.button("🔄 Limpiar resultados", use_container_width=True):
        st.session_state.results = None
        st.rerun()

if demo:
    st.session_state.demo = [
        {"id": 101, "time": 35, "qty": 12},
        {"id": 102, "time": 50, "qty": 10},
        {"id": 103, "time": 25, "qty": 15},
    ]
    st.rerun()

defaults = st.session_state.get("demo", [])
st.markdown("### ✍️ Registra los productos")
st.write("Completa el número único, el tiempo de fabricación en minutos y la cantidad producida.")
rows = []
cols = st.columns(2)
for i in range(int(n)):
    d = defaults[i] if i < len(defaults) else {"id": i + 1, "time": 0, "qty": 0}
    with cols[i % 2]:
        with st.container(border=True):
            st.markdown(f"**Producto {i + 1}**")
            a, b, c = st.columns(3)
            pid = a.number_input("N.º producto", min_value=1, value=int(d["id"]), step=1, key=f"id_{i}")
            mins = b.number_input("Tiempo (min)", min_value=0, max_value=1440, value=int(d["time"]), step=1, key=f"time_{i}")
            qty = c.number_input("Cantidad", min_value=0, value=int(d["qty"]), step=1, key=f"qty_{i}")
            rows.append({"Producto": int(pid), "Tiempo (min)": int(mins), "Cantidad": int(qty)})

if st.button("📊 Calcular resultados", type="primary", use_container_width=True):
    if any(r["Tiempo (min)"] < 1 for r in rows):
        st.error("Cada tiempo debe estar entre 1 y 1440 minutos.")
    elif any(r["Cantidad"] < 1 for r in rows):
        st.error("La cantidad producida debe ser un entero positivo.")
    elif len({r["Producto"] for r in rows}) != len(rows):
        st.error("Hay números de producto repetidos. Cada producto debe tener un número único.")
    else:
        df = pd.DataFrame(rows)
        avg = df["Tiempo (min)"].mean()
        df["Diferencia (min)"] = df["Tiempo (min)"] - avg
        df["Estado"] = df["Diferencia (min)"].apply(lambda x: "Retrasado" if x > 0 else ("Eficiente" if x < 0 else "En el promedio"))
        late = int((df["Estado"] == "Retrasado").sum())
        pct = late * 100 / len(df)
        maxrow = df.loc[df["Tiempo (min)"].idxmax()]
        if late == 0:
            recommendation = "Proceso estable: ningún producto supera el promedio. Mantén el método de trabajo actual."
        elif pct <= 50:
            recommendation = "Retrasos moderados: revisa corte, costura, terminado o empaque de los productos que superan el promedio."
        else:
            recommendation = "Retrasos críticos: más de la mitad supera el promedio. Evalúa reorganizar el flujo de trabajo y la asignación de tareas."
        st.session_state.results = {"df": df, "avg": avg, "units": int(df["Cantidad"].sum()), "late": late, "pct": pct, "maxrow": maxrow, "sumtime": int(df["Tiempo (min)"].sum()), "recommendation": recommendation}
        st.session_state.pop("demo", None)

res = st.session_state.results
if res:
    st.divider()
    st.markdown("## 🌷 Resultados del análisis")
    st.caption("El promedio se calcula por producto registrado, como en tu algoritmo original.")
    st.metric("Tiempo promedio de fabricación", f'{res["avg"]:.2f} minutos')
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Unidades producidas", f'{res["units"]:,}'.replace(",", "."))
    c2.metric("Productos sobre el promedio", f'{res["late"]} de {len(res["df"])}', f'{res["pct"]:.1f}% del lote')
    c3.metric("Mayor tiempo de fabricación", f'{int(res["maxrow"]["Tiempo (min)"])} min', f'Producto {int(res["maxrow"]["Producto"])}')
    c4.metric("Tiempo total registrado", f'{res["sumtime"]:,} min'.replace(",", "."))
    st.markdown("### Detalle por producto")
    display_df = res["df"].copy()
    display_df["Diferencia (min)"] = display_df["Diferencia (min)"].map(lambda x: f"{x:+.2f}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    st.info("💡 **Recomendación del sistema:** " + res["recommendation"])
    st.download_button("⬇️ Descargar resultados CSV", data=res["df"].to_csv(index=False).encode("utf-8-sig"), file_name="analisis_tiempos_produccion.csv", mime="text/csv")
else:
    st.info("👈 Registra los datos y pulsa **Calcular resultados** para ver el análisis aquí.")

st.divider()
st.caption("TiempoLab · Proyecto académico de Ingeniería Industrial · Datos procesados durante la sesión.")
