# Documentación del MEF Data Lake

Bienvenido a la documentación oficial del **MEF Data Lake**, un pipeline ETL completo para procesar y consolidar datos presupuestales del Ministerio de Economía y Finanzas (MEF) y el INEI (Perú), procesados localmente a través de PySpark.

## Objetivo del Proyecto

Centralizar, limpiar y estandarizar datos abiertos dispersos (API CKAN de SIAF y SISMEPRE, archivos ZIP históricos del RENAMU) en un único repositorio de datos optimizado en formato Parquet, organizado mediante la arquitectura Medallion.

Este Data Lake utiliza herramientas nativas de procesamiento de datos de Big Data (Apache Spark) sin depender de servicios en la nube costosos o bases de datos monolíticas.

## Índice de Contenidos

- **[Arquitectura del Sistema](arquitectura.md)**: Conoce el diseño técnico, herramientas y flujos generales.
- **Capas de Procesamiento (Medallion)**:
  - **[1. Capa Bronze (Ingesta)](capas/bronze.md)**: Extracción de datos crudos desde fuentes del gobierno.
  - **[2. Capa Silver (Limpieza)](capas/silver.md)**: Curación, normalización de datos y cálculo de banderas de calidad.
  - **[3. Capa Gold (Modelado Dimensional)](capas/gold.md)**: Estructuración de datos para análisis (Star Schema, EAV).
- **[Gestión de Calidad de Datos (DQ)](calidad_datos.md)**: Reglas y banderas utilizadas para auditar la fiabilidad del presupuesto y las métricas municipales.
- **[Integración con Power BI](integracion_powerbi.md)**: Guía paso a paso para conectar, limpiar y relacionar los datos de la capa Gold utilizando Power Query (M).

