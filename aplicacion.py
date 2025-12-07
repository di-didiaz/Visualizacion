import streamlit as st
import pandas as pd
import altair as alt
from streamlit_option_menu import option_menu
import joblib
import numpy as np


# Crear pagina
st.set_page_config(page_title="Conoce y predice la Salud de España", page_icon="⚕️", layout="wide")

# Subir datos- metodo tomado de app de prueba de Streamlit
@st.cache_data
def load_data():
    df = pd.read_csv("datos/df_final.csv", encoding= "latin-1")
    return df

 #Se uso como referencia  https://www.youtube.com/watch?v=7E3yxq-P-a8
with st.sidebar:
    selected = option_menu(menu_title="Menú", options=["Resultados de la encuesta", "Predicción personalizada"], icons=["clipboard-pulse", "stars"], 
                           menu_icon="body-text",default_index=1)
###########################################################################################################
# Pagina de inicio
if selected == "Resultados de la encuesta":
    st.title("Análisis y Predicción de datos de Salud")
    st.write("""Esta sección te permite visualizar resultados de la
             [Encuesta de Salud de España 2023](https://www.sanidad.gob.es/estadEstudios/estadisticas/encuestaSaludEspana/home.htm).""")
    st.subheader("Datos por comunidad")

    df=load_data()
    
    tab1, tab2 = st.tabs(["Salud", "Sedentarismo"]) # Referencia de https://docs.streamlit.io/develop/api-reference/charts/st.altair_chart
    with tab1:

        st.subheader("🗺️ Haz clic en una comunidad autónoma")
        df_prop = (df.groupby(["Comunidad Autonoma", "Salud_Percibida"]).size().reset_index(name="count"))

        # Proporcion por comunidad
        total_comunidad = df_prop.groupby("Comunidad Autonoma")["count"].transform("sum")
        df_prop["prop"] = df_prop["count"]/total_comunidad

        mapa= alt.Chart(df_prop).mark_bar().encode(x=alt.X("prop:Q", title="Proporción"),y=alt.Y("Comunidad Autonoma:N", sort='-x'), color=alt.Color("Salud_Percibida:N", title="Salud percibida"),
                                                          tooltip=["Comunidad Autonoma", "Salud_Percibida", alt.Tooltip("prop:Q", format=".2f")]).properties(width=800, height=600).interactive()
        st.altair_chart(mapa)
        
    with tab2:


        st.subheader("Horas del dia sentado en los encuestados")
    
        sedentarismo= alt.Chart(df).mark_bar().encode(alt.X("Sedentarismo%_horas:Q",bin= True, title= "Horas sentado"), alt.Y("count()")).properties(width=600, height=400).interactive()

        st.altair_chart(sedentarismo,user_container_width=True)                                                            

                                                                    
        st.dataframe(df.head()) #https://www.youtube.com/watch?v=7E3yxq-P-a8

###########################################################################################################

# Sección Predecir percepción de salud
if selected == "Predicción personalizada":
    st.title("Predecir mis riesgos de salud")
    st.subheader("Aquí podrás predecir tus riesgos de salud segun los datos de la población en España")

    df = load_data()
    catboost= joblib.load("datos/catboost_slt.joblib")
    modord= joblib.load("datos/modelo_ord_slt.joblib")
    preprocesador= joblib.load("datos/preprocesador_slt.joblib")

# Entradas de los usuarions
    st.markdown("Introduce los datos abajo para obtener la predicción.")
    edad= st.slider("👶 Selecciona tu edad", 0, 100, 35)
    comunidad= st.selectbox("Comunidad Autónoma", ["País Vasco", "Castilla - La Mancha", "Comunitat Valenciana",
       "Andalucía", "Castilla y León", "Extremadura", "Balears, Illes","Cataluña", "Galicia", "Aragón", "Rioja, La","Madrid, Comunidad de", "Murcia, Región de",
       "Navarra, Comunidad Foral de", "Asturias, Principado de","Canarias", "Cantabria", "Ceuta", "Melilla"])
    estudios= st.selectbox("👩‍🏫 Que estudios tienes?",["Enseñanzas profesionales de grado medio o equivalentes", "Educación Primaria completa", "Estudios de Bachillerato", "Primera etapa de Enseñanza Secundaria, con o sin título (2º ESO aprobado, EGB, Bachillerato Elemental)",
                                                   "Enseñanzas profesionales de grado superior o equivalentes", "Estudios universitarios o equivalentes"])
    actividad= st.selectbox( "💪Cuantas veces a la semana haces actividad física?", ["Activo", "Ocasional", "Regular", "Sedentario"])
    # Esto hay que cambiarlo despues a ["1 o 2 veces", "3 veces", "4 o mas veces", "Nunca"] para volverlo a hacer  ["Activo", "Ocasional", "Regular", "Sedentario"])

    horas_sentado=st.number_input("🦥 Cuántas horas pasas sentado al dia en un dia normal?",min_value=0, max_value=24, value=4)
    sedentarismo= horas_sentado/24
    carne_frec= st.selectbox("🥩 Cuántas piezas de carne comes como máximo a la semana?. Si comes más de 10, elije 10",[0,0.5, 1.5, 3,5,7,10], index=3)

    if st.button("Predecir ahora!"):
        df_entrada= pd.DataFrame([{"Edad": edad, "Comunidad Autonoma": comunidad, "Estudios": estudios,  "Actividad_física_cat": actividad, "Sedentarismo%_horas": sedentarismo, "Carne_frec": carne_frec}])

        
        cat_pred= catboost.predict(df_entrada)[0]
        cat_prob= catboost.predict_proba(df_entrada)[0].max()

        ord_pred= modord.predict(df_entrada)[0]
        ord_prob= modord.predict_proba(df_entrada)[0].max()

        noms= {0: "Malo",1: "Regular",2: "Bueno"}
        cat_prediccion= noms[int(cat_pred)]
        mod_prediccion= noms[int(ord_pred)]
        
        st.subheader("Tus resultados")
        
        st.subheader("Prediccón Catboost→ "+cat_prediccion+"(confianza:"+ str(round(cat_prob, 2)))
        st.subheader("Prediccion Ordinal→ "+ mod_prediccion+"(confianza:"+str(round(ord_prob, 2)))

        st.success("Predicción generada")

