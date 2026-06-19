# Integración con Power BI Desktop

Este documento describe cómo conectar y cargar las tablas de la capa **Gold** (tanto el Modelo Estrella de la ejecución presupuestal del SIAF como el modelo EAV del RENAMU) en Power BI Desktop utilizando los archivos Parquet locales de nuestro Data Lake.

---

## El Problema de los Archivos de Control de Spark (`_SUCCESS`)

Cuando Apache Spark escribe DataFrames en formato Parquet, genera archivos auxiliares de metadatos en las carpetas de destino:
1. El archivo `_SUCCESS` (un archivo vacío de 0 bytes que indica que la escritura finalizó correctamente).
2. Archivos checksum ocultos (`.part-*.crc`).

Si intentas cargar una carpeta completa en Power BI utilizando el conector estándar de carpetas sin filtros adicionales, Power BI intentará procesar **todos los archivos** del directorio. Al encontrarse con el archivo `_SUCCESS`, arrojará el siguiente error:

> **DataFormat.Error:** Parquet.Document: class parquet::ParquetInvalidOrCorruptedFileException (message: 'Invalid: Parquet magic bytes not found in footer. Either the file is corrupted or this is not a parquet file.')

### Solución
La solución consiste en aplicar un paso en **Power Query (M)** que filtre y conserve únicamente aquellos archivos cuyo campo `Extension` sea exactamente `.parquet` antes de combinar o extraer su contenido.

---

## Configuración de las Consultas en Power Query (M)

A continuación se detalla el código M para cada una de las tablas de la capa Gold. 

Para utilizarlos en Power BI Desktop:
1. Ve a **Inicio** -> **Transformar Datos** (*Transform Data*).
2. Haz clic derecho en el panel izquierdo de consultas -> **Nueva Consulta** -> **Consulta en blanco** (*Blank Query*).
3. Selecciona la nueva consulta, ve a **Inicio** -> **Editor avanzado** (*Advanced Editor*).
4. Reemplaza todo el contenido con el código correspondiente de abajo y renombra la consulta.
5. *(Opcional)* Modifica la ruta base `C:\Users\ANGEL\angelariasus\mef_dl\data\gold\` si tu almacenamiento local está en una ruta diferente.

### 1. `dim_tiempo`
```powerquery
let
    Origen = Folder.Files("C:\Users\ANGEL\angelariasus\mef_dl\data\gold\dim_tiempo"),
    SoloParquet = Table.SelectRows(Origen, each ([Extension] = ".parquet")),
    ObtenerContenido = Table.AddColumn(SoloParquet, "Personalizado", each Parquet.Document([Content])),
    #"Se expandió Personalizado" = Table.ExpandTableColumn(ObtenerContenido, "Personalizado", 
        {"SK_Tiempo", "Ano", "Mes", "Nombre_Mes", "Trimestre", "Semestre"}, 
        {"SK_Tiempo", "Ano", "Mes", "Nombre_Mes", "Trimestre", "Semestre"}
    ),
    #"Tipo cambiado" = Table.TransformColumnTypes(#"Se expandió Personalizado",{
        {"SK_Tiempo", Int64.Type}, 
        {"Ano", Int64.Type}, 
        {"Mes", Int64.Type}, 
        {"Nombre_Mes", type text}, 
        {"Trimestre", Int64.Type}, 
        {"Semestre", Int64.Type}
    })
in
    #"Tipo cambiado"
```

### 2. `dim_geografia`
```powerquery
let
    Origen = Folder.Files("C:\Users\ANGEL\angelariasus\mef_dl\data\gold\dim_geografia"),
    SoloParquet = Table.SelectRows(Origen, each ([Extension] = ".parquet")),
    ObtenerContenido = Table.AddColumn(SoloParquet, "Personalizado", each Parquet.Document([Content])),
    #"Se expandió Personalizado" = Table.ExpandTableColumn(ObtenerContenido, "Personalizado", 
        {"SK_Geografia", "Cod_Departamento", "Nombre_Departamento", "Cod_Provincia", "Nombre_Provincia", "Cod_Distrito", "Nombre_Distrito"}, 
        {"SK_Geografia", "Cod_Departamento", "Nombre_Departamento", "Cod_Provincia", "Nombre_Provincia", "Cod_Distrito", "Nombre_Distrito"}
    ),
    #"Tipo cambiado" = Table.TransformColumnTypes(#"Se expandió Personalizado",{
        {"SK_Geografia", Int64.Type}, 
        {"Cod_Departamento", type text}, 
        {"Nombre_Departamento", type text},
        {"Cod_Provincia", type text}, 
        {"Nombre_Provincia", type text}, 
        {"Cod_Distrito", type text}, 
        {"Nombre_Distrito", type text}
    })
in
    #"Tipo cambiado"
```

### 3. `dim_municipalidad`
```powerquery
let
    Origen = Folder.Files("C:\Users\ANGEL\angelariasus\mef_dl\data\gold\dim_municipalidad"),
    SoloParquet = Table.SelectRows(Origen, each ([Extension] = ".parquet")),
    ObtenerContenido = Table.AddColumn(SoloParquet, "Personalizado", each Parquet.Document([Content])),
    #"Se expandió Personalizado" = Table.ExpandTableColumn(ObtenerContenido, "Personalizado", 
        {"SK_Municipalidad", "Cod_Nivel_Gobierno", "Nivel_Gobierno", "Cod_Sector", "Sector", "Cod_Pliego", "Pliego", "Cod_Ejecutora", "Ejecutora", "Sec_Ejecutora", "Categoria_Municipal"}, 
        {"SK_Municipalidad", "Cod_Nivel_Gobierno", "Nivel_Gobierno", "Cod_Sector", "Sector", "Cod_Pliego", "Pliego", "Cod_Ejecutora", "Ejecutora", "Sec_Ejecutora", "Categoria_Municipal"}
    ),
    #"Tipo cambiado" = Table.TransformColumnTypes(#"Se expandió Personalizado",{
        {"SK_Municipalidad", Int64.Type}, 
        {"Cod_Nivel_Gobierno", type text}, 
        {"Nivel_Gobierno", type text},
        {"Cod_Sector", type text}, 
        {"Sector", type text}, 
        {"Cod_Pliego", type text}, 
        {"Pliego", type text},
        {"Cod_Ejecutora", type text}, 
        {"Ejecutora", type text}, 
        {"Sec_Ejecutora", type text}, 
        {"Categoria_Municipal", type text}
    })
in
    #"Tipo cambiado"
```

### 4. `dim_clasificacion_ingreso`
```powerquery
let
    Origen = Folder.Files("C:\Users\ANGEL\angelariasus\mef_dl\data\gold\dim_clasificacion_ingreso"),
    SoloParquet = Table.SelectRows(Origen, each ([Extension] = ".parquet")),
    ObtenerContenido = Table.AddColumn(SoloParquet, "Personalizado", each Parquet.Document([Content])),
    #"Se expandió Personalizado" = Table.ExpandTableColumn(ObtenerContenido, "Personalizado", 
        {"SK_Clasificacion", "Cod_Generica", "Generica", "Cod_Subgenerica", "Subgenerica", "Cod_Subgenerica_Det", "Subgenerica_Det", "Cod_Especifica", "Especifica", "Cod_Especifica_Det", "Especifica_Det"}, 
        {"SK_Clasificacion", "Cod_Generica", "Generica", "Cod_Subgenerica", "Subgenerica", "Cod_Subgenerica_Det", "Subgenerica_Det", "Cod_Especifica", "Especifica", "Cod_Especifica_Det", "Especifica_Det"}
    ),
    #"Tipo cambiado" = Table.TransformColumnTypes(#"Se expandió Personalizado",{
        {"SK_Clasificacion", Int64.Type}, 
        {"Cod_Generica", type text}, 
        {"Generica", type text},
        {"Cod_Subgenerica", type text}, 
        {"Subgenerica", type text}, 
        {"Cod_Subgenerica_Det", type text}, 
        {"Subgenerica_Det", type text},
        {"Cod_Especifica", type text}, 
        {"Especifica", type text}, 
        {"Cod_Especifica_Det", type text}, 
        {"Especifica_Det", type text}
    })
in
    #"Tipo cambiado"
```

### 5. `dim_financiamiento`
```powerquery
let
    Origen = Folder.Files("C:\Users\ANGEL\angelariasus\mef_dl\data\gold\dim_financiamiento"),
    SoloParquet = Table.SelectRows(Origen, each ([Extension] = ".parquet")),
    ObtenerContenido = Table.AddColumn(SoloParquet, "Personalizado", each Parquet.Document([Content])),
    #"Se expandió Personalizado" = Table.ExpandTableColumn(ObtenerContenido, "Personalizado", 
        {"SK_Financiamiento", "Cod_Fuente_Financiamiento", "Fuente_Financiamiento", "Cod_Rubro", "Rubro", "Cod_Tipo_Recurso", "Tipo_Recurso"}, 
        {"SK_Financiamiento", "Cod_Fuente_Financiamiento", "Fuente_Financiamiento", "Cod_Rubro", "Rubro", "Cod_Tipo_Recurso", "Tipo_Recurso"}
    ),
    #"Tipo cambiado" = Table.TransformColumnTypes(#"Se expandió Personalizado",{
        {"SK_Financiamiento", Int64.Type}, 
        {"Cod_Fuente_Financiamiento", type text}, 
        {"Fuente_Financiamiento", type text},
        {"Cod_Rubro", type text}, 
        {"Rubro", type text}, 
        {"Cod_Tipo_Recurso", type text}, 
        {"Tipo_Recurso", type text}
    })
in
    #"Tipo cambiado"
```

### 6. `fact_ejecucion_presupuestal`
```powerquery
let
    Origen = Folder.Files("C:\Users\ANGEL\angelariasus\mef_dl\data\gold\fact_ejecucion_presupuestal"),
    SoloParquet = Table.SelectRows(Origen, each ([Extension] = ".parquet")),
    ObtenerContenido = Table.AddColumn(SoloParquet, "Personalizado", each Parquet.Document([Content])),
    #"Se expandió Personalizado" = Table.ExpandTableColumn(ObtenerContenido, "Personalizado", 
        {"SK_Tiempo", "SK_Geografia", "SK_Municipalidad", "SK_Clasificacion", "SK_Financiamiento", "SK_Calidad", "Monto_PIA", "Monto_PIM", "Monto_Recaudado", "Brecha_Presupuestal", "Tasa_Avance", "Estado_Avance"}, 
        {"SK_Tiempo", "SK_Geografia", "SK_Municipalidad", "SK_Clasificacion", "SK_Financiamiento", "SK_Calidad", "Monto_PIA", "Monto_PIM", "Monto_Recaudado", "Brecha_Presupuestal", "Tasa_Avance", "Estado_Avance"}
    ),
    #"Tipo cambiado" = Table.TransformColumnTypes(#"Se expandió Personalizado",{
        {"SK_Tiempo", Int64.Type}, 
        {"SK_Geografia", Int64.Type}, 
        {"SK_Municipalidad", Int64.Type}, 
        {"SK_Clasificacion", Int64.Type}, 
        {"SK_Financiamiento", Int64.Type}, 
        {"SK_Calidad", Int64.Type},
        {"Monto_PIA", type number}, 
        {"Monto_PIM", type number}, 
        {"Monto_Recaudado", type number}, 
        {"Brecha_Presupuestal", type number}, 
        {"Tasa_Avance", type number}, 
        {"Estado_Avance", type text}
    })
in
    #"Tipo cambiado"
```

### 7. `stg_renamu` (Esquema EAV de RENAMU)
```powerquery
let
    Origen = Folder.Files("C:\Users\ANGEL\angelariasus\mef_dl\data\gold\stg_renamu"),
    SoloParquet = Table.SelectRows(Origen, each ([Extension] = ".parquet")),
    ObtenerContenido = Table.AddColumn(SoloParquet, "Personalizado", each Parquet.Document([Content])),
    #"Se expandió Personalizado" = Table.ExpandTableColumn(ObtenerContenido, "Personalizado", 
        {"Ubigeo", "Departamento", "Provincia", "Distrito", "ccdd", "ccdi", "ccpp", "idmunici", "ANO_RENAMU", "pregunta", "respuesta"}, 
        {"Ubigeo", "Departamento", "Provincia", "Distrito", "ccdd", "ccdi", "ccpp", "idmunici", "ANO_RENAMU", "pregunta", "respuesta"}
    ),
    #"Tipo cambiado" = Table.TransformColumnTypes(#"Se expandió Personalizado",{
        {"Ubigeo", type text}, 
        {"Departamento", type text}, 
        {"Provincia", type text}, 
        {"Distrito", type text}, 
        {"ccdd", type text}, 
        {"ccdi", type text}, 
        {"ccpp", type text}, 
        {"idmunici", type text}, 
        {"ANO_RENAMU", Int64.Type}, 
        {"pregunta", type text}, 
        {"respuesta", type text}
    })
in
    #"Tipo cambiado"
```

---

## Relaciones del Modelo de Datos (Star Schema)

Una vez cargadas las tablas, ve a la vista de **Modelo** en Power BI y crea las relaciones del Star Schema. Todas las relaciones deben ser del tipo **1 a Muchos (1:*)**, donde el lado "1" corresponde a la dimensión y el lado "Muchos (*)" a la tabla de hechos `fact_ejecucion_presupuestal`.

La dirección del filtro cruzado debe ser **Única** (de la dimensión hacia los hechos).

| Tabla Dimensión (Lado 1) | Campo Dimensión | Tabla Hechos (Lado *) | Campo Hechos |
|--------------------------|-----------------|-----------------------|--------------|
| `dim_tiempo`             | `SK_Tiempo`     | `fact_ejecucion_presupuestal` | `SK_Tiempo`  |
| `dim_geografia`          | `SK_Geografia`  | `fact_ejecucion_presupuestal` | `SK_Geografia` |
| `dim_municipalidad`      | `SK_Municipalidad` | `fact_ejecucion_presupuestal` | `SK_Municipalidad` |
| `dim_clasificacion_ingreso` | `SK_Clasificacion` | `fact_ejecucion_presupuestal` | `SK_Clasificacion` |
| `dim_financiamiento`     | `SK_Financiamiento` | `fact_ejecucion_presupuestal` | `SK_Financiamiento` |
