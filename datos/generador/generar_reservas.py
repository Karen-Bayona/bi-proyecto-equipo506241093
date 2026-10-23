#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F3 - Reservas SINTETICAS de Hotelera Caribe S.A.S. (cadena ficticia, Cartagena de Indias).

DECLARACION: todos los datos que produce este script son sinteticos. No hay personas
reales ni datos personales: cada fila es una reserva de habitacion sin huesped identificado.

Calibracion con datos reales (para que no sea aleatorio):
  - F2 (EMA, DANE): ocupacion mensual de Cartagena -> ocupacion objetivo de la cadena.
  - F1 (Migracion Colombia): entradas mensuales de extranjeros por el aeropuerto de
    Cartagena -> estacionalidad de la proporcion de huespedes extranjeros, y paises de
    nacionalidad -> reparto de nacionalidades.

Uso (desde la raiz del repositorio):
    python datos/generador/generar_reservas.py

Entradas  (en datos/raw/):
    anex-EMA-2023-2024-2025.xlsx            (hoja "4.2 Porc Mens Ocupación.reg")
    Comportamiento_mensual_Ext2023/2024/2025.csv   (tableros de Migracion, uno por anio)
    Mapa_pais_de_nacionalidad_Ext2023/2024/2025.csv (tableros de Migracion, uno por anio)
    (el script busca por patron, asi que tolera espacios o guiones bajos en el nombre)
Salidas:
    datos/raw/F3_reservas_hotelera_caribe.csv
    datos/muestras/F3_reservas_muestra.csv  (20 filas)
    datos/generador/inconsistencias_introducidas.md
Dependencias: pip install numpy pandas openpyxl
"""
import glob
import os
import sys
from datetime import date, timedelta

import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------
# Parametros (todos ficticios y editables)
# ----------------------------------------------------------------------------
SEMILLA = 42
INICIO = date(2023, 1, 1)
FIN = date(2025, 12, 31)
BURN_IN_DIAS = 10                 # dias previos para que el hotel no arranque vacio
PROB_CANCELACION = 0.09           # proporcion de reservas canceladas
EXTRANJEROS_BASE = 0.33           # 33 % de visitantes extranjeros (texto de la seccion 1.1)

# hotel: (nombre, zona, habitaciones por tipo, factor de ocupacion frente al destino)
HOTELES = {
    "H1": ("Caribe Heroico Centro", "Centro Historico", {"Estandar": 35, "Superior": 15, "Suite": 5}, 1.03),
    "H2": ("Caribe Heroico Murallas", "Centro Historico", {"Estandar": 40, "Superior": 15, "Suite": 5}, 0.98),
    "H3": ("Caribe Heroico Getsemani", "Getsemani", {"Estandar": 40, "Superior": 15, "Suite": 5}, 1.00),
    "H4": ("Caribe Heroico Bocagrande", "Bocagrande", {"Estandar": 80, "Superior": 30, "Suite": 10}, 0.99),
    "H5": ("Caribe Heroico Laguito", "Bocagrande", {"Estandar": 85, "Superior": 30, "Suite": 10}, 1.01),
}
ZONAS_BOCAGRANDE = {"H4", "H5"}

# Tarifa base por noche en COP, SIN impuestos, en 2023
TARIFA_BASE = {"Estandar": 280_000, "Superior": 380_000, "Suite": 620_000}
FACTOR_HOTEL_TARIFA = {"H1": 1.25, "H2": 1.20, "H3": 1.22, "H4": 0.95, "H5": 0.92}
INFLACION_ANUAL = {2023: 1.00, 2024: 1.07, 2025: 1.12}   # supuesto ficticio
IVA = 0.19

NOCHES_VALORES = [1, 2, 3, 4, 5, 7]
NOCHES_PROBS = [0.20, 0.30, 0.25, 0.12, 0.07, 0.06]
NOCHES_MEDIA = float(np.dot(NOCHES_VALORES, NOCHES_PROBS))

CANALES = ["Web directa", "OTA", "Agencia", "Corporativo", "Walk-in"]
CANALES_PROBS = [0.28, 0.40, 0.17, 0.10, 0.05]
ANTICIPACION_MEDIA = {"Web directa": 18, "OTA": 25, "Agencia": 55, "Corporativo": 12, "Walk-in": 0}
CANCEL_FACTOR = {"Web directa": 0.8, "OTA": 1.5, "Agencia": 0.7, "Corporativo": 0.6, "Walk-in": 0.0}

# Inconsistencias introducidas a proposito (el enunciado lo exige cuando los datos llegan limpios)
PROB_DUPLICADO = 0.015
PROB_NULO = {"canal": 0.04, "nacionalidad": 0.06, "num_huespedes": 0.02}
CODIGOS_TIPO = {
    "H1": {"Estandar": "Estándar", "Superior": "Superior", "Suite": "Suite"},
    "H2": {"Estandar": "Estándar", "Superior": "Superior", "Suite": "Suite"},
    "H3": {"Estandar": "STD", "Superior": "SUP", "Suite": "SUITE"},
    "H4": {"Estandar": "estandar", "Superior": "superior", "Suite": "suite"},
    "H5": {"Estandar": ["Standard", "estandar"], "Superior": ["Superior", "sup."], "Suite": ["Suite", "ste"]},
}

RAIZ = os.getcwd()
RAW = os.path.join(RAIZ, "datos", "raw")
MUESTRAS = os.path.join(RAIZ, "datos", "muestras")
GENERADOR = os.path.join(RAIZ, "datos", "generador")


# ----------------------------------------------------------------------------
# Calendario de festivos de Colombia (Ley Emiliani), sin dependencias externas
# ----------------------------------------------------------------------------
def pascua(anio):
    a = anio % 19
    b, c = divmod(anio, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes, dia = divmod(h + l - 7 * m + 114, 31)
    return date(anio, mes, dia + 1)


def lunes_siguiente(d):
    return d if d.weekday() == 0 else d + timedelta(days=(7 - d.weekday()) % 7)


def festivos(anio):
    p = pascua(anio)
    fijos = [date(anio, 1, 1), date(anio, 5, 1), date(anio, 7, 20), date(anio, 8, 7),
             date(anio, 12, 8), date(anio, 12, 25), p - timedelta(days=3), p - timedelta(days=2)]
    movibles = [date(anio, 1, 6), date(anio, 3, 19), date(anio, 6, 29), date(anio, 8, 15),
                date(anio, 10, 12), date(anio, 11, 1), date(anio, 11, 11),
                p + timedelta(days=39), p + timedelta(days=60), p + timedelta(days=68)]
    return set(fijos) | {lunes_siguiente(d) for d in movibles}


# ----------------------------------------------------------------------------
# Lectura de datos reales para calibrar
# ----------------------------------------------------------------------------
def leer_ocupacion_ema():
    """Devuelve {(anio, mes): ocupacion 0-1} de Cartagena desde la hoja 4.2 de la EMA."""
    from openpyxl import load_workbook
    ruta = glob.glob(os.path.join(RAW, "anex-EMA*.xlsx"))
    if not ruta:
        sys.exit("No encuentro el anexo de la EMA en datos/raw/ (anex-EMA*.xlsx).")
    ws = load_workbook(ruta[0], data_only=True)["4.2 Porc Mens Ocupación.reg"]
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto",
             "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    encabezado = col = None
    ocup, anio = {}, None
    for fila in ws.iter_rows(values_only=True):
        if fila[0] == "Año":                       # fila de encabezado
            encabezado = [str(x).strip() if x is not None else "" for x in fila]
            col = encabezado.index("Cartagena")
            continue
        if encabezado is None:
            continue
        if fila[0] is not None:                    # el anio solo aparece en enero
            anio = int(float(fila[0]))
        if fila[1] in meses and fila[col] is not None:
            ocup[(anio, meses.index(fila[1]) + 1)] = float(fila[col]) / 100.0
    return ocup


def _entero(txt):
    txt = txt.strip().replace(",", "").replace(".", "")
    return int(txt) if txt else None


def leer_entradas_migracion():
    """Perfil mensual de entradas de extranjeros (promedio de los anios disponibles)."""
    perfiles = []
    rutas = sorted(glob.glob(os.path.join(RAW, "Comportamiento*mensual*Ext*.csv")))
    if not rutas:
        sys.exit("No encuentro los CSV de comportamiento mensual de Migracion en datos/raw/ "
                 "(patron: Comportamiento*mensual*Ext*.csv).")
    print("Comportamiento mensual (F1):", [os.path.basename(r) for r in rutas])
    for ruta in rutas:
        filas = [l.split("\t") for l in open(ruta, encoding="utf-16").read().splitlines()]
        valores = [_entero(x) for x in filas[3][1:] if x.strip()]
        entradas = valores[0::2]
        if len(entradas) == 12:
            perfiles.append(np.array(entradas, dtype=float))
    if not perfiles:
        sys.exit("Los archivos de comportamiento mensual no tienen 12 meses de entradas.")
    perfil = np.mean([p / p.mean() for p in perfiles], axis=0)
    return perfil


def leer_paises_migracion():
    """Paises de nacionalidad (excluye Colombia) con su peso, de los tableros de Migracion."""
    pesos = {}
    rutas = sorted(glob.glob(os.path.join(RAW, "Mapa*nacionalidad*Ext*.csv")))
    if not rutas:
        sys.exit("No encuentro los CSV de pais de nacionalidad de Migracion en datos/raw/ "
                 "(patron: Mapa*nacionalidad*Ext*.csv).")
    print("Pais de nacionalidad (F1):", [os.path.basename(r) for r in rutas])
    for ruta in rutas:
        d = pd.read_csv(ruta, encoding="utf-16", sep="\t", dtype=str)
        for pais, total in zip(d.iloc[:, 1], d.iloc[:, -1]):
            pesos[pais] = pesos.get(pais, 0) + _entero(total)
    pesos.pop("Colombia", None)
    if len(pesos) < 20:
        sys.exit("Se leyeron muy pocos paises: revisa los archivos de nacionalidad en datos/raw/.")
    paises = list(pesos)
    p = np.array([pesos[x] for x in paises], dtype=float)
    return paises, p / p.sum()


# ----------------------------------------------------------------------------
# Generacion
# ----------------------------------------------------------------------------
def generar():
    rng = np.random.default_rng(SEMILLA)
    ocup_ema = leer_ocupacion_ema()
    perfil_mig = leer_entradas_migracion()
    paises, pesos_paises = leer_paises_migracion()

    dias = [INICIO - timedelta(days=BURN_IN_DIAS) + timedelta(days=i)
            for i in range((FIN - INICIO).days + 1 + BURN_IN_DIAS)]
    indice = {d: i for i, d in enumerate(dias)}
    fest = set()
    for a in range(INICIO.year, FIN.year + 1):
        fest |= festivos(a)

    filas = []
    ocupadas = {}   # (hotel, tipo) -> array de habitaciones ocupadas por dia
    for h, (_, _, tipos, _) in HOTELES.items():
        for t in tipos:
            ocupadas[(h, t)] = np.zeros(len(dias) + 10, dtype=int)

    for h, (_, _, tipos, factor) in HOTELES.items():
        for t, n_hab in tipos.items():
            occ = ocupadas[(h, t)]
            for d in dias:
                mes_ref = (d.year, d.month)
                if mes_ref not in ocup_ema:           # dias del burn-in (dic 2022)
                    mes_ref = (INICIO.year, 12) if (INICIO.year, 12) in ocup_ema else (INICIO.year, 1)
                objetivo = ocup_ema[mes_ref] * factor
                objetivo *= {4: 1.08, 5: 1.08, 0: 0.94, 1: 0.94}.get(d.weekday(), 1.0)
                if d in fest:
                    objetivo *= 1.06
                objetivo = min(max(objetivo, 0.25), 0.97)
                n = rng.poisson(n_hab * objetivo / NOCHES_MEDIA)
                for _ in range(n):
                    noches = int(rng.choice(NOCHES_VALORES, p=NOCHES_PROBS))
                    i0 = indice[d]
                    if (occ[i0:i0 + noches] >= n_hab).any():
                        continue                      # sin capacidad
                    occ[i0:i0 + noches] += 1
                    filas.append((h, t, d, noches))

    # Reservas confirmadas -> atributos
    df = pd.DataFrame(filas, columns=["hotel", "tipo", "entrada", "noches"])
    df = df[df["entrada"] >= INICIO].reset_index(drop=True)
    n = len(df)
    df["estado"] = "Confirmada"

    # Canceladas adicionales (no ocupan capacidad)
    n_cancel = int(n * PROB_CANCELACION / (1 - PROB_CANCELACION))
    extra = df.sample(n=n_cancel, random_state=SEMILLA, replace=False).copy()
    extra["estado"] = "Cancelada"
    df = pd.concat([df, extra], ignore_index=True)
    n = len(df)

    df["canal"] = rng.choice(CANALES, size=n, p=CANALES_PROBS)
    # las canceladas se inclinan a OTA/Agencia
    mask = df["estado"] == "Cancelada"
    pesos_c = np.array([CANCEL_FACTOR[c] for c in CANALES]) * np.array(CANALES_PROBS)
    pesos_c = pesos_c / pesos_c.sum()
    df.loc[mask, "canal"] = rng.choice(CANALES, size=int(mask.sum()), p=pesos_c)

    antic = np.array([rng.exponential(ANTICIPACION_MEDIA[c]) if ANTICIPACION_MEDIA[c] > 0 else 0
                      for c in df["canal"]]).round().astype(int)
    df["fecha_reserva"] = [e - timedelta(days=int(a)) for e, a in zip(df["entrada"], antic)]
    df["salida"] = [e + timedelta(days=int(k)) for e, k in zip(df["entrada"], df["noches"])]

    # Nacionalidad segun estacionalidad de llegadas (F1) y reparto de paises (F1)
    prop_ext = np.clip(EXTRANJEROS_BASE * perfil_mig[df["entrada"].map(lambda x: x.month - 1)], 0.15, 0.55)
    es_ext = rng.random(n) < prop_ext
    df["nacionalidad"] = "Colombia"
    df.loc[es_ext, "nacionalidad"] = rng.choice(paises, size=int(es_ext.sum()), p=pesos_paises)

    df["num_huespedes"] = rng.choice([1, 2, 3, 4], size=n, p=[0.22, 0.52, 0.16, 0.10])

    # Tarifa por noche en COP: tarifa base x hotel x inflacion x temporada x festivo
    def tarifa(fila_hotel, fila_tipo, f_entrada):
        ocup = ocup_ema.get((f_entrada.year, f_entrada.month), 0.65)
        temporada = min(max(1 + 1.0 * (ocup - 0.65), 0.80), 1.30)
        extra_fest = 1.10 if f_entrada in fest else 1.0
        base = (TARIFA_BASE[fila_tipo] * FACTOR_HOTEL_TARIFA[fila_hotel]
                * INFLACION_ANUAL[f_entrada.year] * temporada * extra_fest)
        return base
    base = np.array([tarifa(h, t, e) for h, t, e in zip(df["hotel"], df["tipo"], df["entrada"])])
    base = base * rng.normal(1.0, 0.04, size=n)
    # Inconsistencia: Bocagrande reporta CON IVA, Centro/Getsemani SIN IVA
    con_iva = df["hotel"].isin(ZONAS_BOCAGRANDE).to_numpy()
    df["tarifa_noche"] = np.where(con_iva, base * (1 + IVA), base).round(-3).astype(int)
    df["tarifa_total"] = df["tarifa_noche"] * df["noches"]

    df = df.sort_values(["entrada", "hotel"]).reset_index(drop=True)
    df.insert(0, "id_reserva", [f"RES-{i + 1:06d}" for i in range(len(df))])
    return df, ocup_ema


def introducir_inconsistencias(df, rng):
    """Aplica defectos de calidad y devuelve (df_sucio, registro_para_el_informe)."""
    reg = {}
    # 1) Codigos de tipo de habitacion distintos por hotel
    def codigo(h, t):
        c = CODIGOS_TIPO[h][t]
        return c if isinstance(c, str) else rng.choice(c)
    df["tipo_habitacion"] = [codigo(h, t) for h, t in zip(df["hotel"], df["tipo"])]
    df = df.drop(columns=["tipo"])

    # 2) Nulos
    for col, p in PROB_NULO.items():
        idx = df.sample(frac=p, random_state=int(rng.integers(1e9))).index
        df[col] = df[col].astype(object)
        df.loc[idx, col] = None
        reg[f"nulos_{col}"] = len(idx)

    # 3) Formatos de fecha por zona (se escriben como texto)
    def fmt(col):
        out = []
        for h, v in zip(df["hotel"], df[col]):
            out.append(v.strftime("%m-%d-%Y") if h in ZONAS_BOCAGRANDE else v.strftime("%d/%m/%Y"))
        return out
    df["fecha_reserva"] = fmt("fecha_reserva")
    df["fecha_entrada"] = fmt("entrada")
    df["fecha_salida"] = fmt("salida")
    df = df.drop(columns=["entrada", "salida"])

    # 4) Duplicados exactos
    dup = df.sample(frac=PROB_DUPLICADO, random_state=int(rng.integers(1e9)))
    reg["duplicados"] = len(dup)
    df = pd.concat([df, dup], ignore_index=True).sort_values("id_reserva", kind="stable").reset_index(drop=True)

    columnas = ["id_reserva", "hotel", "tipo_habitacion", "fecha_reserva", "fecha_entrada",
                "fecha_salida", "noches", "num_huespedes", "canal", "nacionalidad",
                "tarifa_noche", "tarifa_total", "estado"]
    return df[columnas], reg


def informe(df_limpio, df, reg, ocup_ema):
    """Escribe el informe con ejemplos REALES tomados del archivo generado."""
    L = ["# F3 - Inconsistencias introducidas a proposito (datos SINTETICOS)\n",
         f"Reservas generadas: {len(df):,} filas (incluye {reg['duplicados']:,} duplicados). "
         f"Periodo: {INICIO} a {FIN}. Semilla: {SEMILLA}.\n"]
    ej = lambda cond, n=2: df[cond].head(n).to_string(index=False)

    L.append("## 1. Formatos de fecha distintos por zona")
    L.append("Centro Historico y Getsemani: dd/mm/aaaa. Bocagrande: mm-dd-aaaa.\n```")
    L.append(df[df["hotel"].isin(["H1", "H4"])].head(4)[["id_reserva", "hotel", "fecha_reserva", "fecha_entrada"]].to_string(index=False))
    L.append("```\n")
    L.append("## 2. Identificadores duplicados")
    dups = df[df.duplicated("id_reserva", keep=False)].head(4)
    L.append(f"{reg['duplicados']:,} filas repetidas exactamente.\n```")
    L.append(dups[["id_reserva", "hotel", "fecha_entrada", "tarifa_noche"]].to_string(index=False))
    L.append("```\n")
    L.append("## 3. Valores nulos")
    L.append(f"canal: {reg['nulos_canal']:,}; nacionalidad: {reg['nulos_nacionalidad']:,}; "
             f"num_huespedes: {reg['nulos_num_huespedes']:,}.\n```")
    L.append(df[df["canal"].isna()].head(3)[["id_reserva", "hotel", "canal", "nacionalidad"]].to_string(index=False))
    L.append("```\n")
    L.append("## 4. Codigos de tipo de habitacion inconsistentes")
    L.append("Valores distintos para el mismo tipo: " + ", ".join(sorted(df["tipo_habitacion"].unique())) + ".\n")
    L.append("## 5. Tarifa con y sin IVA (sin columna que lo indique)")
    L.append("Bocagrande (H4, H5) incluye IVA 19 %; Centro y Getsemani (H1-H3) no. "
             "Promedio de tarifa_noche por hotel:\n```")
    L.append(df.groupby("hotel")["tarifa_noche"].mean().round(0).astype(int).to_string())
    L.append("```\n")

    # Calibracion: ocupacion lograda vs EMA
    L.append("## Calibracion con la EMA (ocupacion mensual de Cartagena)")
    hab_total = sum(sum(t.values()) for _, _, t, _ in HOTELES.values())
    conf = df_limpio[df_limpio["estado"] == "Confirmada"].copy()
    conf["mes"] = pd.to_datetime(conf["entrada"]).dt.to_period("M")
    filas = []
    for p, g in conf.groupby("mes"):
        d_mes = p.days_in_month
        noches = g["noches"].sum()
        filas.append((str(p), round(100 * noches / (hab_total * d_mes), 1),
                      round(100 * ocup_ema.get((p.year, p.month), np.nan), 1)))
    cal = pd.DataFrame(filas, columns=["mes", "ocupacion_cadena_%", "ocupacion_EMA_Cartagena_%"])
    cal["diferencia"] = (cal.iloc[:, 1] - cal.iloc[:, 2]).round(1)
    L.append("```")
    L.append(cal.to_string(index=False))
    L.append("```")
    return "\n".join(L), cal


def main():
    os.makedirs(MUESTRAS, exist_ok=True)
    os.makedirs(GENERADOR, exist_ok=True)
    df_limpio, ocup_ema = generar()
    rng = np.random.default_rng(SEMILLA + 1)
    df, reg = introducir_inconsistencias(df_limpio.copy(), rng)

    salida = os.path.join(RAW, "F3_reservas_hotelera_caribe.csv")
    df.to_csv(salida, index=False, encoding="utf-8")
    df.sample(20, random_state=SEMILLA).sort_values("id_reserva").to_csv(
        os.path.join(MUESTRAS, "F3_reservas_muestra.csv"), index=False, encoding="utf-8")
    texto, cal = informe(df_limpio, df, reg, ocup_ema)
    with open(os.path.join(GENERADOR, "inconsistencias_introducidas.md"), "w", encoding="utf-8") as f:
        f.write(texto)
    print(f"Filas: {len(df):,} | Periodo: {INICIO} a {FIN}")
    print(f"Diferencia media absoluta de ocupacion frente a la EMA: {cal['diferencia'].abs().mean():.1f} puntos")
    print("Archivos escritos en datos/raw, datos/muestras y datos/generador")


if __name__ == "__main__":
    main()
