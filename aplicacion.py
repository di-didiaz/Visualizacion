import streamlit as st
import pandas as pd
import altair as alt
from streamlit_option_menu import option_menu
import joblib
import numpy as np
import plotly.express as px
import json


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

        st.subheader("Haz clic en una comunidad autónoma para...")

        # ver https://discuss.streamlit.io/t/interactive-maps/82782
        df_prop = (df.groupby(["Comunidad Autonoma", "Salud_Percibida"]).size().reset_index(name="count"))

        # Proporcion por comunidad
        total_comunidad = df_prop.groupby("Comunidad Autonoma")["count"].transform("sum")
        df_prop["prop"] = df_prop["count"]/total_comunidad

        with open("datos/spain-communities.geojson") as r:
            geoson_mapa= json.load(r)
        df_mapa= (df.groupby("Comunidad Autonoma")["IMC"].mean().reset_index())

        mapaccaa= px.choropleth(df_mapa, geojson= geoson_mapa, locations="Comunidad Autonoma",
                                featureidkey="properties.name", color="IMC",hover_name="Comunidad Autonoma",
                                title="Puntuación mas alta de salud", color_continuous_scale="Viridis")
        mapaccaa.update_geos(fitbounds="locations", visible=False)

        event= st.plotly_chart(mapaccaa, on_select="rerun",selection_mode=["points","box","lasso"])
        points= event["selection"].get("points",[])
        if points:
            first_point= points[0]
            sigla = first_point["properties"].get("sigla", None)
        else:
            sigla = None


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

        st.altair_chart(sedentarismo,use_container_width=True)                                                            

                                                                    
        st.dataframe(df.head()) #https://www.youtube.com/watch?v=7E3yxq-P-a8

###########################################################################################################

# Sección Predecir percepción de salud
if selected == "Predicción personalizada":
    st.title("Mis riesgos de salud")
    st.subheader("Introduce tus datos para predecir si tienes riesgo de padecer de Hipertension, Diabetes y Colesterol")
    st.caption("Recuerda: Estas predicciones no son diagnosticos de salud.")

    df = load_data()
    diabetes= joblib.load("datos/diabetes.joblib")
    hipertension= joblib.load("datos/hipertension.joblib")
    colesterol= joblib.load("datos/colesterol.joblib")
    preprocesador= joblib.load("datos/preprocesador_slt.joblib")

# Entradas de los usuarions
    st.markdown("---------------------------")
    edad= st.slider("Selecciona tu edad", 15, 100, 35, help="Desliza el punto hasta llegar a tu edad")
    altura= st.slider("Introduce tu altura estimada en centímetros", 80, 165, 210,help="Desliza el punto hasta llegar a tu altura")  
    peso= st.number_input("Introduce tu peso estimado en kilos", 35, 200, 70, help="Usa un estimado o tu última medición")
    imc= peso/(altura**2)
    estudios= st.selectbox("Selecciona tu nivel de estudios",["Enseñanzas profesionales de grado medio o equivalentes", "Educación Primaria completa", "Estudios de Bachillerato", "Primera etapa de Enseñanza Secundaria, con o sin título (2º ESO aprobado, EGB, Bachillerato Elemental)",
                                                   "Enseñanzas profesionales de grado superior o equivalentes", "Estudios universitarios o equivalentes"])
    sedentarismo=st.number_input("Horas que pasas sentadx en un dia",min_value=0, max_value=24, value=4)
    Refrescos_frec= st.selectbox("Numero de refrescos que bebes normalmente en una la semana. Si bebes más de 10, elije 10",[0,0.5, 1.5, 3,5,7,10], index=3, help="Las medidas intermedias significan que bebes un refresco y medio")

    if st.button("Predecir ahora!"):
        df_entrada= pd.DataFrame([{"Edad": edad, 'IMC': imc,"Estudios": estudios, "Refrescos_frec": Refrescos_frec,  "Sedentarismo%_horas": sedentarismo, "Peso": peso, "Altura": altura}])

        
        diabetes_pred= diabetes.predict(df_entrada)[0]
        diabetes_prob= diabetes.predict_proba(df_entrada)[0].max()

        hipertension_pred= hipertension.predict(df_entrada)[0]
        hipertension_prob= hipertension.predict_proba(df_entrada)[0].max()

        colesterol_pred= colesterol.predict(df_entrada)[0]
        colesterol_prob= colesterol.predict_proba(df_entrada)[0].max()

        noms= {0: "Genial, no tienes riesgo",1: "Hay riesgo, revisa las recomendaciones abajo"}
        diabetes_prediccion= noms[int(diabetes_pred)]
        hipertension_prediccion= noms[int(hipertension_pred)]
        colesterol_prediccion= noms[int(colesterol_pred)]
        
        st.subheader("Tus resultados")
        
        st.subheader("Tu probabilidad de padecer de diabetes es de → "+ str(round(diabetes_prob, 2)+"."+diabetes_pred))
        st.subheader("Tu probabilidad de padecer de hipertension es de → "+ str(round(hipertension_prob, 2)+"."+hipertension_pred))
        st.subheader("Tu probabilidad de padecer de colesterol es de → "+ str(round(colesterol_prob, 2)+"."+colesterol_pred))
        

        st.success("Predicción generada")

