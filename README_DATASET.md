# Diccionario de Variables - Dataset de Torniquetes
## Dataset de Series de Tiempo para Predicción de Fallas en Equipos de Borde

---

## 📋 Información General

- **Archivo**: `dataset_torniquetes_completo.csv`
- **Registros**: 75,072
- **Periodo**: Enero 2024 - Junio 2025 (18 meses)
- **Granularidad**: 30 minutos (solo horas pico: 06:00-10:00 y 17:00-21:00)
- **Días**: Solo días hábiles (lunes a viernes)
- **Equipos**: 12 (8 Torniquetes + 4 Máquinas de Autoservicio)
- **Estaciones**: 4 (Puerto, Viña del Mar, Quilpué, Limache)

---

## 📊 Variables del Dataset (12 columnas)

### 1. **FECHA_HORA**
- **Tipo**: Timestamp (datetime)
- **Descripción**: Marca temporal del registro
- **Formato**: `YYYY-MM-DD HH:MM:SS`
- **Rango**: 2024-01-01 06:00:00 hasta 2025-06-30 20:30:00
- **Frecuencia**: Intervalos de 30 minutos
- **Ejemplo**: `2024-03-15 08:30:00`
- **Valores únicos**: 6,256 timestamps

**Uso**: Variable temporal para análisis de series de tiempo, feature engineering (extraer hora, día de semana, mes, etc.)

---

### 2. **ESTACION**
- **Tipo**: Categórica (String)
- **Descripción**: Nombre de la estación donde se encuentra el equipo
- **Valores posibles**: 
  - `Puerto` (inicio de ruta, afluencia base)
  - `Viña del Mar` (alta afluencia 1.5x)
  - `Quilpué` (alta afluencia 1.4x)
  - `Limache` (fin de ruta, afluencia moderada 0.8x)
- **Ejemplo**: `Viña del Mar`
- **Distribución**: 18,768 registros por estación (balanceada)

**Uso**: Identificar patrones de afluencia por ubicación geográfica. Las estaciones centrales tienen mayor tráfico.

---

### 3. **ID_EQUIPO**
- **Tipo**: String (identificador único)
- **Descripción**: Código identificador del equipo específico
- **Formato**: `TUR-XX` (Torniquetes) o `MAS-XX` (Máquinas Autoservicio)
  - Primera letra indica la estación: **P**uerto, **V**iña, **Q**uilpué, **L**imache
  - Número indica el equipo: 1, 2, 3...
- **Valores posibles** (12 equipos):
  - **Puerto**: TUR-P1, TUR-P2, MAS-P1
  - **Viña del Mar**: TUR-V1, TUR-V2, MAS-V1
  - **Quilpué**: TUR-Q1, TUR-Q2, MAS-Q1
  - **Limache**: TUR-L1, TUR-L2, MAS-L1
- **Ejemplo**: `TUR-V1` (Torniquete 1 en Viña del Mar)
- **Distribución**: 6,256 registros por equipo

**Uso**: Identificador único para análisis por equipo individual, tracking de historial de fallas específicas.

---

### 4. **TIPO_EQUIPO**
- **Tipo**: Categórica (String)
- **Descripción**: Clasificación del tipo de equipo
- **Valores posibles**:
  - `Torniquete` (8 equipos, 50,048 registros)
  - `Máquina Autoservicio` (4 equipos, 25,024 registros)
- **Ejemplo**: `Torniquete`

**Características por tipo**:
- **Torniquetes**: Alto tráfico (promedio 226 transacciones/hora, rango 0-575)
- **Máquinas Autoservicio**: Bajo tráfico (promedio 5 transacciones/hora, rango 0-12)

**Uso**: Diferencial importante, cada tipo tiene patrones de falla distintos y volúmenes de uso muy diferentes.

---

### 5. **TRANSACCIONES_HORA** ⭐
- **Tipo**: Numérico (entero)
- **Descripción**: Número real de transacciones/pasajeros procesados en ese periodo de 30 minutos
- **Rango**: 
  - Torniquetes: 0 a 575
  - MAS: 0 a 12
- **Promedio**:
  - Torniquetes: 226 transacciones/periodo
  - MAS: 5 transacciones/periodo
- **Ejemplo**: `245` (torniquete procesó 245 pasajeros en 30 min)

**Interpretación**:
- **0**: Equipo completamente fuera de servicio (falla total)
- **< Promedio -15%**: Posible degradación del equipo
- **> Promedio +15%**: Posible compensación por falla de equipo vecino

**Uso**: Variable principal para detectar anomalías y patrones de falla. Es el indicador más directo del estado operativo.

---

### 6. **PROM_HIST_HORA** 📈
- **Tipo**: Numérico (entero)
- **Descripción**: Promedio histórico de transacciones para ese equipo en ese día de semana y hora específica (línea base de comparación)
- **Rango**: Similar a TRANSACCIONES_HORA
- **Cálculo**: Promedio esperado basado en:
  - Equipo específico
  - Día de la semana (lunes-viernes)
  - Hora del día
- **Ejemplo**: `230` (se esperan 230 transacciones en promedio)

**Uso**: Línea base para calcular anomalías. Permite detectar desviaciones del comportamiento normal esperado.

---

### 7. **ANOMALIA_USO** ⚠️ (KEY FEATURE)
- **Tipo**: Numérico (float, 2 decimales)
- **Descripción**: Desviación porcentual entre las transacciones reales y el promedio histórico
- **Fórmula**: `((TRANSACCIONES_HORA - PROM_HIST_HORA) / PROM_HIST_HORA) × 100`
- **Rango**: -100% a +100%
- **Promedio**: 1.38%
- **Ejemplo**: `-25.50` (25.5% menos transacciones que lo esperado)

**Interpretación crítica**:
| Rango | Significado | Acción |
|-------|-------------|--------|
| **> +10%** | Uso superior al normal | Posible compensación por falla de equipo vecino |
| **0% ± 10%** | Uso normal | Operación estándar ✓ |
| **-15% a -30%** | ⚠️ Alerta Temprana | Degradación inicial (2 días antes de falla) |
| **-50% a -90%** | 🚨 Alerta Máxima | Degradación severa (1 día antes de falla) |
| **-100%** | 🔴 Falla Total | Equipo fuera de servicio |

**Uso**: **Feature más importante** para predicción. Indicador directo de salud del equipo.

---

### 8. **DIAS_DESDE_ULTIMO_MANT** 🔧
- **Tipo**: Numérico (entero)
- **Descripción**: Días transcurridos desde el último mantenimiento correctivo del equipo
- **Rango**: 0 a 180+ días
- **Inicialización**: Aleatorio entre 30-180 días al inicio del dataset
- **Ejemplo**: `45` (hace 45 días se hizo mantenimiento)

**Comportamiento**:
- Se **incrementa** continuamente durante operación normal
- Se **resetea a 0** tras una falla total (mantenimiento correctivo)
- Mayor valor → Mayor desgaste acumulado → Mayor probabilidad de falla

**Uso**: Indicador de desgaste. Equipos sin mantenimiento reciente tienen mayor riesgo de falla.

---

### 9. **DIAS_DESDE_ULTIMA_ALERTA**
- **Tipo**: Numérico (entero)
- **Descripción**: Días transcurridos desde que se emitió la última alerta preventiva para ese equipo
- **Rango**: 0 a 999 días
- **Inicialización**: 999 (sin alertas previas)
- **Ejemplo**: `3` (hace 3 días hubo una alerta)

**Comportamiento**:
- Se **resetea a 0** cuando hay alerta temprana o máxima (anomalía < -15%)
- Se **resetea a 0** tras falla total
- Se **incrementa** cuando no hay alertas

**Uso**: Evitar alertas repetitivas. Útil para entender el historial reciente de eventos del equipo.

---

### 10. **CLIMA_LLUVIA** 🌧️
- **Tipo**: Binario (0/1)
- **Descripción**: Indicador de condición climática del día
- **Valores**:
  - `0` = Sin lluvia (81.8% de los días)
  - `1` = Con lluvia (18.2% de los días)
- **Ejemplo**: `1` (llovió ese día)

**Impacto en afluencia**:
- Cuando llueve, las transacciones se reducen ~15% (multiplicador 0.85x)
- Afecta a todas las estaciones por igual

**Uso**: Factor externo que explica variaciones normales de afluencia (no relacionado con fallas del equipo).

---

### 11. **FALLA_TIPO**
- **Tipo**: Categórica (String)
- **Descripción**: Tipo de falla observada en el equipo en ese momento
- **Valores posibles**:
  - `Ninguna` (97.63% - 73,296 registros) - Operación normal
  - `Falla Lenta` (1.62% - 1,216 registros) - Degradación progresiva
  - `Falla Total` (0.75% - 560 registros) - Equipo fuera de servicio
- **Ejemplo**: `Falla Lenta`

**Relación con ANOMALIA_USO**:
- **Ninguna**: ANOMALIA_USO ≈ normal (±15%)
- **Falla Lenta**: ANOMALIA_USO entre -15% y -90%
- **Falla Total**: ANOMALIA_USO = -100%

**Uso**: Variable de diagnóstico. Útil para entrenamiento supervisado y análisis post-mortem de fallas.

---

### 12. **FALLA_INMINENTE_7D** 🎯 (TARGET)
- **Tipo**: Binario (0/1)
- **Descripción**: **Variable objetivo** - indica si el equipo tendrá una falla total en los próximos 7 días
- **Valores**:
  - `0` = No habrá falla (93.71% - 70,352 registros)
  - `1` = Habrá falla total en ≤ 7 días (6.29% - 4,720 registros)
- **Ejemplo**: `1` (este equipo fallará en los próximos 7 días)

**Características del target**:
- **Desbalanceado**: Solo 6.29% de casos positivos (realista para predicción de fallas)
- **Ventana de predicción**: 7 días de anticipación
- **Se activa**: Desde 7 días antes hasta el momento de la falla total
- **Se desactiva**: Inmediatamente después de la falla total

**Uso**: 
- **Variable a predecir** en modelos de Machine Learning
- Objetivo: Clasificación binaria (falla vs no falla)
- Métrica recomendada: Recall, F1-Score, AUC-ROC (NO usar accuracy por desbalance)

---

## 🔗 Relaciones Entre Variables

### Cadena de Detección de Fallas
```
DIAS_DESDE_ULTIMO_MANT ↑ 
        ↓
TRANSACCIONES_HORA ↓
        ↓
ANOMALIA_USO ↓ (< -15%)
        ↓
FALLA_TIPO = "Falla Lenta"
        ↓
FALLA_INMINENTE_7D = 1
        ↓
FALLA_TIPO = "Falla Total"
```

### Efecto Valla (Compensación)
Cuando un equipo falla en una estación:
```
Equipo A: TRANSACCIONES_HORA ↓↓ (falla)
Equipo B (mismo tipo): TRANSACCIONES_HORA ↑ (+10% a +30%)
Equipo B: ANOMALIA_USO > +10% (compensación)
```

### Variables Temporales vs Operacionales

**Temporales** (contexto externo):
- FECHA_HORA
- CLIMA_LLUVIA

**Operacionales** (estado del equipo):
- TRANSACCIONES_HORA
- ANOMALIA_USO
- DIAS_DESDE_ULTIMO_MANT
- FALLA_TIPO

**Identificadores**:
- ESTACION
- ID_EQUIPO
- TIPO_EQUIPO

---

## 📈 Estadísticas Clave

| Variable | Tipo | Valores Únicos | Nulos | Rango |
|----------|------|----------------|-------|-------|
| FECHA_HORA | Timestamp | 6,256 | 0 | 2024-01-01 a 2025-06-30 |
| ESTACION | Categórica | 4 | 0 | - |
| ID_EQUIPO | String | 12 | 0 | - |
| TIPO_EQUIPO | Categórica | 2 | 0 | - |
| TRANSACCIONES_HORA | Numérico | Variable | 0 | 0-575 |
| PROM_HIST_HORA | Numérico | Variable | 0 | Similar a TRANSACCIONES |
| ANOMALIA_USO | Numérico | Variable | 0 | -100.00% a +100.00% |
| DIAS_DESDE_ULTIMO_MANT | Entero | Variable | 0 | 0-180+ |
| DIAS_DESDE_ULTIMA_ALERTA | Entero | Variable | 0 | 0-999 |
| CLIMA_LLUVIA | Binario | 2 | 0 | 0, 1 |
| FALLA_TIPO | Categórica | 3 | 0 | - |
| FALLA_INMINENTE_7D | Binario | 2 | 0 | 0, 1 |

**✓ Dataset completo sin valores nulos**

---

## 💡 Recomendaciones de Uso

### Features Más Importantes (por orden)
1. **ANOMALIA_USO** - Indicador directo de salud
2. **TRANSACCIONES_HORA** - Volumen de uso actual
3. **DIAS_DESDE_ULTIMO_MANT** - Desgaste acumulado
4. **TIPO_EQUIPO** - Patrones diferentes por tipo
5. **PROM_HIST_HORA** - Contexto de normalidad

### Feature Engineering Recomendado
De FECHA_HORA extraer:
- `hora` (6-21)
- `dia_semana` (0-4)
- `es_hora_pico_mañana` (bool)
- `es_hora_pico_tarde` (bool)
- `mes` (1-12)

Rolling windows de ANOMALIA_USO:
- Media móvil de 3 horas
- Desviación estándar de 6 horas
- Tendencia de 24 horas

---

## 📞 Información del Dataset

**Versión**: 1.0  
**Fecha de generación**: Noviembre 2025  
**Registros**: 75,072  
**Columnas**: 12  
**Formato**: CSV (UTF-8 con BOM)
