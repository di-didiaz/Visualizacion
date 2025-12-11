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
                           menu_icon="body-text",default_index=0)
###########################################################################################################
# Pagina de resutlados iniciales

if selected == "Resultados de la encuesta":

    df= load_data()
    st.title("Análisis y visualización de la Encuesta de Salud de España 2023")
    st.write("""Esta sección te permite visualizar datos de la
             [Encuesta de Salud de España 2023](https://www.sanidad.gob.es/estadEstudios/estadisticas/encuestaSaludEspana/home.htm).""")
    st.text("Algunas métricas relevantes:")

    lac_prom= df['Lacteos_frec'].mean(skipna=True)
    hsentado_prom=df['Sedentarismo%_horas'].mean(skipna=True)
    porc_hipert=df['Hipertension_bin'].mean(skipna=True)*100
    
    # Se usa como referencia https://www.corecode.school/en/blog/python-streamlit

    col1,col2,col3=st.columns(3)

    col1.metric(label="Consumo de carne promedio", value=f"{lac_prom:.2f}")
    col2.metric(label="Promedio de horas sentados/dia", value=f"{hsentado_prom:.2f}")
    col3.metric(label="Porcentaje de personas hipertensas", value=f"{porc_hipert:.2f}%")

    st.markdown("---------------------------")

 #####################################################################
 # Tabs   
  
    tab1, tab2, tab3= st.tabs(["Composición Física", "Salud percibida", "Determinantes de Salud"]) # Referencia de https://docs.streamlit.io/develop/api-reference/charts/st.altair_chart

###### Tab 1 ####### 
    with tab1:

        st.header("Composición fisica por comunidad autonoma")
        st.caption(" El IMC es la medida de XYZ importante porque XYZ") 

        df_mapa= df.groupby("Comunidad Autonoma").agg(IMC=('IMC','mean'),Peso=('Peso','mean'), Edad= ('Edad','mean'), n=('IMC','count')).round(2).reset_index()
        
        df_prop = (df.groupby(["Comunidad Autonoma", "Salud_Percibida"]).size().reset_index(name="count"))

        # tomado de https://discuss.streamlit.io/t/interactive-maps/82782
        with open("datos/spain-communities.geojson") as r:
            geoson_mapa= json.load(r)
        
        col_mapa, col_tabla= st.columns([1.3,1], gap="large", vertical_alignment='center')

        with col_mapa:
            st.subheader("Mapa Interactivo") 
            mapaccaa= px.choropleth(df_mapa, geojson= geoson_mapa, locations="Comunidad Autonoma",
                                featureidkey="properties.name", color="IMC",hover_name="Comunidad Autonoma", hover_data={'IMC', 'Peso', 'Edad'}, labels={'IMC': 'Promedio IMC'},
                                title="IMC medio por comunidad autonoma. Haz click y zoom para ver detalles por comunidad", color_continuous_scale="teal")
            mapaccaa.update_geos(fitbounds="locations", visible=False)
            mapaccaa.update_layout(margin={'r':0,'l':0, 'b':0,'t':80})

            event=st.plotly_chart(mapaccaa,width='content', on_click= True)

        with col_tabla:
            st.subheader("Detalle por comunidad")
            comunidad_clicada= None
            if event and "points" in event and len(event["points"])>0:
                comunidad_clicada=event["points"][0].get("location")
            if comunidad_clicada:
                ca_elegida= df[df["Comunidad Autonoma"]==comunidad_clicada]
                tabla_ca=ca_elegida.groupby('Sexo').agg(Encuestados=('Sexo','count'), Peso= ('Peso', 'mean'),Altura=('Altura','mean') , IMC= ('IMC','mean')).round(2).reset_index()
                st.subheader(f"Resultados de {comunidad_clicada}")
                st.dataframe(tabla_ca, hide_index= True) #https://www.youtube.com/watch?v=7E3yxq-P-a8
        

        
 ###### Tab 2 #######       
    with tab2:


        st.subheader("Salud percibida y cronicidad por sexo")
        st.caption("Los encuestados podian reportar el sexo con el que se identificaban y el estado de salud como 'Muy bueno', 'Bueno','Regular','Malo'y 'Muy malo'")
        salud_per=df[df['Salud_Percibida'].notna()]
        
        mb_bueno= salud_per['Salud_Percibida'].str.contains('Bueno', case=False, na=False)
        buenos= salud_per.groupby('Sexo').apply(lambda x:mb_bueno.loc[x.index].mean()*100)
       
        cronicidad=df[df['Cronicidad_bin'].notna()]
        cont_cronicidad= cronicidad.groupby('Sexo')['Cronicidad_bin'].mean()*100

        sexos= list(buenos.index)
        st.write("Buena salud percibida por sexos reportados")
        col21, col22= st.columns(2)
        
        col21.metric(label=f"{sexos[0]}", value= f"{buenos.loc[sexos[0]]:.2f}%" )
        col22.metric(f"{sexos[1]}",f"{buenos.loc[sexos[1]]:.2f}%" )

        st.caption("Los encuestados respondieron si padecian de alguna enfermedad crónica")

        col23, col24= st.columns(2)
            
        col23.metric(f"{sexos[0]}",f"{cont_cronicidad.loc[sexos[0]]:.2f}%" )
        col24.metric(f"{sexos[1]}",f"{cont_cronicidad.loc[sexos[1]]:.2f}%" )
                                                                
        st.markdown("----------------")

        st.subheader("Enfermedades crónicas comparadas")
        enfermedades=['Hipertension_bin', 'Diabetes_bin', 'Colesterol_bin']
        enfermedades_dic={"Hipertension":'Hipertension_bin',"Diabetes": 'Diabetes_bin', "Colesterol":'Colesterol_bin'}
        enf_selec=st.multiselect("Selecciona las enfermedades a comparar: ", enfermedades_dic, default=["Diabetes","Hipertension"])
        seleccion_final= [enfermedades_dic[e] for e in enf_selec]

        conteo_enf=df[seleccion_final].sum()
        total_enf= len(df)
        porcentajes_enf= (conteo_enf/total_enf*100).round(2) 

        enf_df=pd.DataFrame({'Enfermedad':enf_selec, 'Total':conteo_enf.values,'Porcentaje':porcentajes_enf.values})

        multi_enf= alt.Chart(enf_df).mark_bar().encode(x=alt.X('Enfermedad', sort=None),y='Total',color='Enfermedad',tooltip=['Enfermedad', 'Total',alt.Tooltip('Porcentaje', format=".2f")]).properties(title="Personas con enfermedades seleccionadas")
        st.altair_chart(multi_enf)
 
 ###### Tab 3 #######   
     
    with tab3:
        st.header("Determinantes de salud: Dieta y actividad física")
        st.caption("Los determinantes de salud son XYZ")

        st.subheader("Frecuencia de alimentación")
        

        carne_prom= df['Carne_frec'].mean()
        refrescos_prom= df['Refrescos_frec'].mean()
        embutidos_prom= df['Embutidos_frec'].mean()
        lacteos_prom= df['Lacteos_frec'].mean()
        verduras_prom= df['Verduras_frec'].mean()
        st.markdown("----------")
        col31, col32, col33, col34, col35= st.columns(5)

        col31.metric(label="Carne", value=f"{lac_prom:.2f}")
        col32.metric(label="Refrescos", value= f"{refrescos_prom:.2f}")
        col33.metric(label= "Embutidos",value=f"{embutidos_prom:.2f}")
        col34.metric(label= "Lacteos", value= f"{lacteos_prom:.2f}")
        col35.metric(label= "Verduras", value= f"{verduras_prom:.2f}")

        st.caption("Promedio de veces a la semana")

        st.markdown("----------")

        lista_frec= ["Carne", "Refrescos", "Embutidos", "Lacteos", "Verduras"]
        frec_lista= {"Carne":"Carne_frec","Refrescos":"Refrescos_frec","Embutidos":"Embutidos_frec", "Lacteos":"Lacteos_frec", "Verduras":"Verduras_frec"}

        opcion= st.selectbox("Selecciona un alimento", lista_frec)
        col_df= frec_lista[opcion]
        lista_colores={"Carne": "#ECDAB2","Refrescos": "#DDBFB3","Embutidos": "#9999C9","Lacteos": "#D8D8EA","Verduras": "#000078"}
        colores=lista_colores[opcion]
        frec_hst= alt.Chart(df).mark_bar(color=colores, binSpacing=0.5).encode(alt.X(col_df,bin=alt.Bin(maxbins=5), title= "Frecuencia de consumo semanal de "), alt.Y("count()", title= "Encuestados")).properties(width=600, height=400, title= "Consumo de "+opcion).interactive()
        st.altair_chart(frec_hst,width='content')

        st.markdown("----------")

        st.subheader("Horas sentados al día")
        # Ver https://www.youtube.com/watch?v=rxWkIn1EZnM
        # https://altair-viz.github.io/gallery/radial_chart.html
        colores_sed=["#73EDFF","#A9B3E0","#6679D8","#4D63D1", "#1724A0", "#030342"]
        df["rangos"]= pd.cut(df["Sedentarismo%_horas"], bins=[0,2,4,6,8,12,24], labels=["0-2 horas","2 a 4 horas","4-6 horas","6 a 8 horas","8 a 12 horas","Mas de 12 hoaas"],include_lowest=True)
        sedentarismo= df["rangos"].value_counts().reset_index()
        sedentarismo.columns= ["Rangos", "Personas"] 

        sedentarismo_pie= alt.Chart(sedentarismo).mark_arc().encode(theta= alt.Theta("Personas", stack= True), color= alt.Color("Rangos:N", scale=alt.Scale(range=colores_sed)), tooltip=["Rangos","Personas"]).properties(width=600, height=600, title= "Porcentaje de horas/dia").interactive()
        etiqueta=(alt.Chart(sedentarismo).mark_text(radius=160, size=12, color= "ghostwhite").encode(theta=alt.Theta("Personas", stack=True),text="Rangos"))
        st.altair_chart(sedentarismo_pie+ etiqueta,width='content')                                                            

                                                                    
        

###########################################################################################################

# Sección Predicción personalizada

if selected == "Predicción personalizada":
    st.title("Mis riesgos de salud")
    st.subheader("Introduce tus datos para predecir el riesgo de padecer de Hipertension, Diabetes y Colesterol")
    st.caption("Recuerda: Estas predicciones son orientativas y no son diagnosticos de salud.")

    df = load_data()
    diabetes_m= joblib.load("datos/diabetes.joblib")
    hipertension_m= joblib.load("datos/hipertension.joblib")
    colesterol_m= joblib.load("datos/colesterol.joblib")
    preprocesado= joblib.load("datos/preprocesador_slt.joblib")

# Entradas de los usuarions
    st.markdown("---------------------------")

    col41, col42, col43, col44, col45= st.columns(5)

    Edad= st.slider("Selecciona tu edad", 15, 100, 35, help="Desliza el punto hasta llegar a tu edad")
    Altura= st.slider("Introduce tu altura estimada en centímetros", 100, 210, 170,help="Desliza el punto hasta llegar a tu altura")  
    Peso= st.number_input("Introduce tu peso estimado en kilos", 32, 200, 70, help="Usa un estimado o tu última medición")
    IMC= Peso/((Altura/100)**2)
    Estudios= st.selectbox("Selecciona tu nivel de estudios",["Enseñanzas profesionales de grado medio o equivalentes", "Educación Primaria completa", "Estudios de Bachillerato", "Primera etapa de Enseñanza Secundaria, con o sin título (2º ESO aprobado, EGB, Bachillerato Elemental)",
                                                   "Enseñanzas profesionales de grado superior o equivalentes", "Estudios universitarios o equivalentes"], help="Incluye el utimo grado que hayas completado")
    Sedentarismo_horas=st.number_input("Horas que pasas sentada en un dia",min_value=0, max_value=24, value=4, help="Horas del dia que normalmente pasas sentada")
    Refrescos_frec= st.selectbox("Numero de refrescos que bebes normalmente en una la semana. Si bebes más de 10, elije 10",[0,0.5, 1.5, 3,5,7,10], index=3, help="Las medidas intermedias indican la mitad de un refresco")

   
    if st.button("Predecir ahora!"):
        df_entrada= pd.DataFrame([{"Edad": Edad, "IMC": IMC,"Refrescos_frec": Refrescos_frec,  "Sedentarismo%_horas": Sedentarismo_horas, "Peso": Peso, "Altura": Altura,"Estudios": Estudios}])
        # error del preprocesador
        df_entrada.loc[0, "Edad"]= int(Edad)
        df_entrada.loc[0, "IMC"]= float(IMC)
        df_entrada.loc[0, "Refrescos_frec"]= float(Refrescos_frec)
        df_entrada.loc[0, "Sedentarismo%_horas"]= float(Sedentarismo_horas)
        df_entrada.loc[0, "Peso"]= float(Peso)
        df_entrada.loc[0, "Altura"]= float(Altura)
        df_entrada.loc[0, "Estudios"]= str(Estudios)

        # procesado incluido en el pipeline df_procesado= preprocesado.transform(df_entrada)
       
        
        diabetes_pred= diabetes_m.predict(df_entrada)[0]
        diabetes_prob= diabetes_m.predict_proba(df_entrada)[0].max()

        hipertension_pred= hipertension_m.predict(df_entrada)[0]
        hipertension_prob= hipertension_m.predict_proba(df_entrada)[0].max()

        colesterol_pred= colesterol_m.predict(df_entrada)[0]
        colesterol_prob= colesterol_m.predict_proba(df_entrada)[0].max()

        noms= {0: "Sin riesgo aparente según modelo",1: "Riesgo detectado: Consultar con un médico"}

               
        st.subheader("Tus resultados")

        col41, col42, col43= st.columns(3)

        with col41:
           st.subheader("Diabetes")
           if diabetes_pred==1:
               st.warning(f"{noms[int(diabetes_pred)]}")
           else:
               st.success(noms[int(diabetes_pred)])
          
           st.write(f"Probablidad: {diabetes_prob*100:.2f}%")
           conteo_digual=(df["Diabetes_bin"] == diabetes_pred).mean()*100
           st.info(f"{conteo_digual:.2f}% de la muestra obtuvieron el mismo resultado")

        with col42:
            st.subheader("Hipertension")
            if hipertension_pred==1:
               st.warning(f"{noms[int(hipertension_pred)]}")
            else:
                st.success(noms[int(hipertension_pred)])
            st.write(f"Probablidad: {hipertension_prob*100:.2f}%")
            conteo_higual=(df["Hipertension_bin"] == hipertension_pred).mean()*100
            st.info(f"{conteo_higual:.2f}% de la muestra obtuvieron el mismo resultado")

        with col43:
            st.subheader("Colesterol")
            if colesterol_pred ==1:
                st.warning(f"{noms[int(colesterol_pred)]}")
            else:
                st.success(noms[int(colesterol_pred)])
            st.write(f"Probablidad: {colesterol_prob*100:.2f}%")
            conteo_cigual=(df["Colesterol_bin"] == colesterol_pred).mean()*100
            st.info(f"{conteo_cigual:.2f}% de la muestra obtuvieron el mismo resultado")

        
        st.markdown("---------")
        st.subheader("Recomendaciones generales")
        st.caption("Recomendaciones orientativas. Siempre consulta con tu médico")

        st.write("Las enfermedades cronicas se pueden manejar XYZ")
        

