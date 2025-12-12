import streamlit as st
import pandas as pd
import altair as alt
from streamlit_option_menu import option_menu
import joblib
import numpy as np
import plotly.express as px
import json


# Crear pagina
st.set_page_config(page_title="Conoce y predice la Salud de España", page_icon="☘", layout="wide")

# Subir datos- metodo tomado de app de prueba de Streamlit
@st.cache_data
def load_data():
    df = pd.read_csv("datos/df_final.csv", encoding= "latin-1")
    return df

 #Se uso como referencia  https://www.youtube.com/watch?v=7E3yxq-P-a8
with st.sidebar:
    selected = option_menu(menu_title="Menú", options=["Resultados de la encuesta", "Predicción personalizada", "Acerca de esta herramienta"], icons=["clipboard-pulse", "stars"], 
                           menu_icon="body-text",default_index=0)
###########################################################################################################
# Pagina de resutlados iniciales

if selected == "Resultados de la encuesta":

    df= load_data()
    st.title("Análisis y visualización de la Encuesta de Salud de España 2023")
    st.info("""Esta sección te permite obtener información sobre los resultados de la
             [Encuesta de Salud de España 2023](https://www.sanidad.gob.es/estadEstudios/estadisticas/encuestaSaludEspana/home.htm).""")
      
    encuestados=len(df)
    col11, col12= st.columns(2)

    with col11: 
        st.subheader("➜ Datos Básicos")
        st.caption('Generalidades de la encuesta')

        with st.container(height=100, border=True): #https://discuss.streamlit.io/t/vertical-divider/62796/4
            cols_mr = st.columns([3.9, 0.2, 3.9,0.2, 3.9])
            with cols_mr[0].container(height=100, border=False):
    
                st.metric("Total personas encuestadas:", f"{encuestados}")
            
            with cols_mr[1]:
                st.markdown(
                    '''
                    <div class="divider-vertical-line"></div>
                    <style>
                        .divider-vertical-line {
                            border-left: 2px solid rgba(49, 51, 63, 0.2);
                            height: 50px;
                            margin: auto;
                        }
                    </style>
                    ''',
                    unsafe_allow_html=True
                            )
        with cols_mr[2].container(height=100, border=False):
            st.metric("Rango de edades:","15 a 110")

        with cols_mr[3]:
                st.markdown(
                    '''
                    <div class="divider-vertical-line"></div>
                    <style>
                        .divider-vertical-line {
                            border-left: 2px solid rgba(49, 51, 63, 0.2);
                            height: 50px;
                            margin: auto;
                        }
                    </style>
                    ''',
                    unsafe_allow_html=True
                            )
        with cols_mr[4].container(height=100, border=False):
            comun=df["Comunidad Autonoma"].nunique()
            st.metric("Comunidades encuestadas:",f"{comun}")
    
   
############    
    with col12:
        lac_prom= df['Lacteos_frec'].mean(skipna=True)
        hsentado_prom=df['Sedentarismo%_horas'].mean(skipna=True)
        porc_hipert=df['Hipertension_bin'].mean(skipna=True)*100
        
        # Se usa como referencia https://www.corecode.school/en/blog/python-streamlit

        st.subheader("➜ Resultados generales de salud y estilo de vida")
        st.caption("Datos destacados")

        with st.container(height=100, border=True): #https://discuss.streamlit.io/t/vertical-divider/62796/4
            cols_mr = st.columns([3.9, 0.2, 3.9,0.2, 3.9])
            with cols_mr[0].container(height=100, border=False):
    
                st.metric(label="Porcentaje de personas hipertensas", value=f"{porc_hipert:.2f}%")
                

            with cols_mr[1]:
                st.markdown(
                    '''
                    <div class="divider-vertical-line"></div>
                    <style>
                        .divider-vertical-line {
                            border-left: 2px solid rgba(49, 51, 63, 0.2);
                            height: 50px;
                            margin: auto;
                        }
                    </style>
                    ''',
                    unsafe_allow_html=True
                            )
        with cols_mr[2].container(height=100, border=False):
            st.metric(label="Promedio de horas sentados/dia", value=f"{hsentado_prom:.2f}")

        with cols_mr[3]:
                st.markdown(
                    '''
                    <div class="divider-vertical-line"></div>
                    <style>
                        .divider-vertical-line {
                            border-left: 2px solid rgba(49, 51, 63, 0.2);
                            height: 50px;
                            margin: auto;
                        }
                    </style>
                    ''',
                    unsafe_allow_html=True
                            )
        with cols_mr[4].container(height=100, border=False):
            st.metric(label="Consumo de lácteos promedio", value=f"{lac_prom:.2f}")
            
    
    st.info("Navega entre las pestañas para más información")         
 #####################################################################
 # Tabs   
  
    tab1, tab2, tab3= st.tabs(["Composición Física", "Salud percibida", "Determinantes de Salud"]) # Referencia de https://docs.streamlit.io/develop/api-reference/charts/st.altair_chart

###### Tab 1 ####### 
    with tab1:

        st.subheader("Composición física por comunidad autonoma")
        st.caption("El indice de masa corporal o IMC es un marcador indirecto de la grasa que puede ayudar a diagnosticar la obesidad. En el caso de los adultos, la OMS define el sobrepeso y la obesidad así: sobrepeso: IMC igual o superior a 25 y obesidad: IMC igual o superior a 30.")
        df_mapa= df.groupby("Comunidad Autonoma").agg(IMC=('IMC','mean'),Peso=('Peso','mean'), Edad= ('Edad','mean'), n=('IMC','count')).round(2).reset_index()
        
        df_prop = (df.groupby(["Comunidad Autonoma", "Salud_Percibida"]).size().reset_index(name="count"))

        # tomado de https://discuss.streamlit.io/t/interactive-maps/82782
        with open("datos/spain-communities.geojson") as r:
            geoson_mapa= json.load(r)
        
       
        with st.container(height=600, border=True): # Metodo tomado de https://discuss.streamlit.io/t/vertical-divider/62796/4
          cols_mr = st.columns([10.9, 0.2, 10.9])
          with cols_mr[0].container(height=550, border=False):

            st.subheader("Mapa")
            st.write("Pasa el cursor sobre las provincias y haz zoom para más detalles") 
            mapaccaa= px.choropleth(df_mapa, geojson= geoson_mapa, locations="Comunidad Autonoma",
                                featureidkey="properties.name", color="IMC",hover_name="Comunidad Autonoma", hover_data={"IMC": True, "Peso": True, "Edad": True}, labels={'IMC': 'Promedio IMC'},
                                color_continuous_scale="teal")
            mapaccaa.update_geos(fitbounds="locations", visible=False)
            mapaccaa.update_layout(margin={'r':0,'l':0, 'b':0,'t':20})

            st.plotly_chart(mapaccaa, width= "content")


        with cols_mr[1]:
            st.markdown(
                    '''
                    <div class="divider-vertical-line"></div>
                    <style>
                        .divider-vertical-line {
                            border-left: 2px solid rgba(49, 51, 63, 0.2);
                            height: 50px;
                            margin: auto;
                        }
                    </style>
                    ''',
                    unsafe_allow_html=True
                            )
        with cols_mr[2].container(height=550, border=False):
            st.subheader("Detalle por comunidad")
            
            comunidades= df["Comunidad Autonoma"].sort_values().unique()
            st.write("Selecciona una comunidad para ver la distribución por sexos")
            comunidad_selec= st.selectbox("Comunidad:", options= comunidades, index=0)

            ca_elegida= df[df["Comunidad Autonoma"]==comunidad_selec]
            tabla_ca=ca_elegida.groupby('Sexo').agg(Encuestados=('Sexo','count'), Peso= ('Peso', 'mean'),Altura=('Altura','mean') , IMC= ('IMC','mean')).round(2).reset_index()
            st.subheader(f"Resultados de {comunidad_selec}")
            st.dataframe(tabla_ca, hide_index= True) #https://www.youtube.com/watch?v=7E3yxq-P-a8

           
        
 ###### Tab 2 #######       
    with tab2:


        st.subheader("Salud percibida y enfermedades por sexo")
        st.info("Los encuestados **reportaron el sexo con el que se identificaban** y el estado de salud como 'Muy bueno', 'Bueno', 'Regular', 'Malo' y 'Muy malo'")
        salud_per=df[df['Salud_Percibida'].notna()]
        
        mb_bueno= salud_per['Salud_Percibida'].str.contains('Bueno| Muy bueno', case=False, na=False)
        buenos= salud_per.groupby('Sexo').apply(lambda x:mb_bueno.loc[x.index].mean()*100)
       
        cronicidad=df[df['Cronicidad_bin'].notna()]
        cont_cronicidad= cronicidad.groupby('Sexo')['Cronicidad_bin'].mean()*100

        sexos= list(buenos.index)
        st.markdown("""**Buena salud**: Percepcion de salud por sexos""")
        col21, col22= st.columns(2)
        
        col21.metric(f"♀ Hombres con buena salud", f"{buenos.loc[sexos[0]]:.2f}%", border=True)
        col22.metric(f"♀ Mujeres con buena salud",f"{buenos.loc[sexos[1]]:.2f}%", border=True )

        st.markdown("""**Enfermedades cronicas**:Padecimiento de enfermedades cronicas por sexo""")
        
        col23, col24= st.columns(2)
            
        col23.metric(f"♀ Hombres con enfermedades cronicas",f"{cont_cronicidad.loc[sexos[0]]:.2f}%", border=True )
        col24.metric(f"♀ Mujeres con enfermedades cronicas",f"{cont_cronicidad.loc[sexos[1]]:.2f}%", border=True )
                                                                
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
        st.write("Son los factores personales, sociales, económicos y ambientales que determinan nuestro estado de salud")

        st.subheader("Frecuencia semanal de consumo de alimentos | Veces ")
        

        carne_prom= df['Carne_frec'].mean()
        refrescos_prom= df['Refrescos_frec'].mean()
        embutidos_prom= df['Embutidos_frec'].mean()
        lacteos_prom= df['Lacteos_frec'].mean()
        verduras_prom= df['Verduras_frec'].mean()
       
        col31, col32, col33, col34, col35= st.columns(5)

        col31.metric(label="Carne", value=f"{lac_prom:.2f}")
        col35.metric(label="Refrescos", value= f"{refrescos_prom:.2f}")
        col34.metric(label= "Embutidos",value=f"{embutidos_prom:.2f}")
        col32.metric(label= "Lacteos", value= f"{lacteos_prom:.2f}")
        col33.metric(label= "Verduras", value= f"{verduras_prom:.2f}")

        st.markdown("----------")
        with st.container(height=450, border=True): # Metodo de https://discuss.streamlit.io/t/vertical-divider/62796/4
            cols_mr = st.columns([10.9, 0.2, 10.9])
            with cols_mr[0].container(height=400, border=False):
             lista_frec= ["Carne", "Refrescos", "Embutidos", "Lacteos", "Verduras"]
             frec_lista= {"Carne":"Carne_frec","Refrescos":"Refrescos_frec","Embutidos":"Embutidos_frec", "Lacteos":"Lacteos_frec", "Verduras":"Verduras_frec"}

             opcion= st.selectbox("Selecciona un alimento", lista_frec)
             col_df= frec_lista[opcion]
             lista_colores={"Carne": "#ECDAB2","Refrescos": "#DDBFB3","Embutidos": "#9999C9","Lacteos": "#D8D8EA","Verduras": "#000078"}
             colores=lista_colores[opcion]
             frec_hst= alt.Chart(df).mark_bar(color=colores, binSpacing=0.5).encode(alt.X(col_df,bin=alt.Bin(maxbins=4), title= "Frecuencia de consumo semanal"), alt.Y("count()", title= "Encuestados")).properties(width=600, height=400, title= "Consumo de "+opcion).interactive()
             st.altair_chart(frec_hst,width='content')

            with cols_mr[1]:
                    st.markdown(
                    '''
                    <div class="divider-vertical-line"></div>
                    <style>
                        .divider-vertical-line {
                            border-left: 2px solid rgba(49, 51, 63, 0.2);
                            height: 400px;
                            margin: auto;
                        }
                    </style>
                    ''',
                    unsafe_allow_html=True
                            )
            with cols_mr[2].container(height=400, border=False):
        
               st.subheader("Alimención saludable según la Organización Mundial de la Salud:")
               st.write("Segun la [OMS](https://www.who.int/es/news-room/fact-sheets/detail/healthy-diet), una dieta sana incluye lo siguiente:")
               st.write("1. Frutas, verduras, legumbres (tales como lentejas y alubias), frutos secos y cereales integrales (por ejemplo, maíz, mijo, avena, trigo o arroz moreno no procesados).")
               st.write("2. Al menos 400 g (o sea, cinco porciones) de frutas y hortalizas al día, excepto papas, batatas, mandioca y otros tubérculos feculentos.")
               st.write("3. Menos del 10% de la ingesta calórica total de azúcares libres, que equivale a 50 gramos (o unas 12 cucharaditas rasas) en el caso de una persona con un peso corporal saludable que consuma aproximadamente 2000 calorías al día, aunque para obtener beneficios de salud adicionales lo ideal sería un consumo inferior al 5% de la ingesta calórica total  Menos del 30% de la ingesta calórica diaria procedente de grasas, en especial las presentes en pescados, aguacates, frutos secos y en los aceites de girasol, soja, canola y oliva en lugar de las grasas en la carne grasa y los productos lácteos de rumiantes tales como vacas, ovejas, cabras y camellos, la mantequilla, el aceite de palma y de coco, la nata, el queso, la mantequilla clarificada y la manteca de cerdo, pizzas congeladas, tartas, galletas, pasteles, obleas, aceites de cocina y pastas untables.")
       
        st.markdown("----------")                                                          
        with st.container(height=650, border=True): # Metodo de https://discuss.streamlit.io/t/vertical-divider/62796/4
            cols_mr = st.columns([10.9, 0.2, 10.9])
            with cols_mr[0].container(height=650, border=False):  
                st.subheader("Actividad física según la OMS")
                st.write("Segun la [OMS](https://www.who.int/es/news/item/25-11-2020-every-move-counts-towards-better-health-says-who), se recomienda:")
                st.write("1. Por lo menos de 150 a 300 minutos de actividad física aeróbica de intensidad moderada o vigorosa por semana para todos los adultos, incluidas las personas que viven con afecciones crónicas o discapacidad.")
                st.write("2. Se aconseja a los adultos de edad avanzada (65 años o más) que añadan actividades destinadas a reforzar el equilibrio y la coordinación, así como el fortalecimiento de los músculos, para ayudar a prevenir las caídas y mejorar la salud.")
                st.write("3. Toda actividad física es beneficiosa y puede realizarse como parte del trabajo, el deporte y el ocio o el transporte (caminar, patinar y montar en bicicleta), pero también del baile, el juego y las tareas domésticas cotidianas, como la jardinería y la limpieza.")
                st.info("La actividad física regular es fundamental para prevenir y ayudar a manejar las cardiopatías, la diabetes de tipo 2 y el cáncer, así como para reducir los síntomas de la depresión y la ansiedad, disminuir el deterioro cognitivo, mejorar la memoria y potenciar la salud cerebral.")


            with cols_mr[1]:
                    st.markdown(
                    '''
                    <div class="divider-vertical-line"></div>
                    <style>
                        .divider-vertical-line {
                            border-left: 2px solid rgba(49, 51, 63, 0.2);
                            height: 400px;
                            margin: auto;
                        }
                    </style>
                    ''',
                    unsafe_allow_html=True
                            )
            with cols_mr[2].container(height=600, border=False):


                st.subheader("Sedentarismo")
                # Ver https://www.youtube.com/watch?v=rxWkIn1EZnM
                # https://altair-viz.github.io/gallery/radial_chart.html
                colores_sed=["#73EDFF","#A9B3E0","#6679D8","#4D63D1", "#1724A0", "#030342"]
                df["rangos"]= pd.cut(df["Sedentarismo%_horas"], bins=[0,2,4,6,8,12,24], labels=["0-2 horas","2 a 4 horas","4-6 horas","6 a 8 horas","8 a 12 horas","Mas de 12 hoaas"],include_lowest=True)
                sedentarismo= df["rangos"].value_counts().reset_index()
                sedentarismo.columns= ["Rangos", "Personas"] 

                sedentarismo_pie= alt.Chart(sedentarismo).mark_arc().encode(theta= alt.Theta("Personas", stack= True), color= alt.Color("Rangos:N", scale=alt.Scale(range=colores_sed)), tooltip=["Rangos","Personas"]).properties(width=600, height=600, title= "Horas sentadas por dia").interactive()
                etiqueta=(alt.Chart(sedentarismo).mark_text(radius=160, size=12, color= "ghostwhite").encode(theta=alt.Theta("Personas", stack=True),text="Rangos"))
                st.altair_chart(sedentarismo_pie+ etiqueta,width='content')                                                            

        

###########################################################################################################

# Sección Predicción personalizada

if selected == "Predicción personalizada":
    st.title("Mis riesgos de salud")
    st.subheader("Introduce tus datos para predecir el riesgo de padecer de Hipertensión, Diabetes y Colesterol")
    st.warning("Recuerda: Estas predicciones son orientativas y no son diagnosticos de salud.")

    df = load_data()
    diabetes_m= joblib.load("datos/diabetes.joblib")
    hipertension_m= joblib.load("datos/hipertension.joblib")
    colesterol_m= joblib.load("datos/colesterol.joblib")
    preprocesado= joblib.load("datos/preprocesador_slt.joblib")

# Entradas de los usuarios
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

        
        st.warning("Los riesgos son orientativos. Siempre consulta con tu médico")
        
##################################


if selected=="Acerca de esta herramienta":

    df= load_data()
    st.image("./datos/logo-uoc-default.png", width=70) # https://www.youtube.com/watch?v=XVRWjCNoH5A
    st.title("Herramienta para la visualización y predicción de datos de salud ")
    st.markdown("""Esta visualización hace parte del Trabajo de Fin de Master **Herramienta interactiva para la visualización y predicción de la relación entre la alimentación y la salud en España a partir de datos abiertos**
                 Esta etapa del proyecto es el desarrollo de una aplicación web de visualización usando como herramienta **Streamlite**. Todo el desarrollo se llevó a cabo **en linea**.""")
    st.info("""El repositorio que contiene los modelos, el preprocesador y los cuadernos de limpieza, exploración, estadística y modelado estan en **https://github.com/di-didiaz/Visualizacion**""")
    st.subheader("La aplicacion permite:")
    st.markdown("""
                1. Visualizar análisis descriptivo del conjunto de datos abiertos de la Encuesta de Salud de España 2023.
                2. Realizar predicciones usando um modelo de entrenado y evaluado""")
    st.markdown("""El conjunto de datos final usado para los resultados de la encuesta tiene la estructura a continuacion:""")

    st.dataframe(df.head(10), hide_index= True)

    st.markdown("""La estructura del conjunto de datos final usado para el modelado se puede previsualizar a continuación""")
    # pd.DataFrame(df.head(10))
    st.markdown("------")
    
    st.markdown("------")   
    

    st.markdown("""**Máster en Ciencia de datos | Universidad Oberta de Catalunya | Diana Díaz G | 2025**""")

    