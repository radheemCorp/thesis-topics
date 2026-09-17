Based on the repository documentation for the **QACM** dataset, the parameters are categorized into **Input Control Parameters (ICPs)**, **Key Performance Indicators (KPIs)**, and their corresponding **Normalized Metrics / QoS Thresholds**:

---

### 1. Input Control Parameters (ICPs)

The dataset includes **8 Input Control Parameters** ($p_1$ to $p_8$) used across the 5 xApps in the experimental model:

* **$p_1$**
* **$p_2$**
* **$p_3$**
* **$p_4$**
* **$p_5$**
* **$p_6$**
* **$p_7$**
* **$p_8$**

---

### 2. Key Performance Indicators (KPIs)

The dataset includes **6 KPIs** generated using Gaussian distribution models based on the ICP inputs:

* **$k_1$**: Generated via $80 \times e^{-\frac{(p_1 + 0)^2}{2 p_2^2}}$
* **$k_2$**: Generated via $100 \times e^{-\frac{(p_1 + p_3)^2}{2 p_2^2}}$
* **$k_3$**: Generated via $120 \times e^{-\frac{(p_1 + 45)^2}{2 p_4^2}}$
* **$k_{41}$**: Generated via $120 \times e^{-\frac{(p_6 + (p_2 - 30))^2}{2 p_5^2}}$
* **$k_{42}$**: Generated via $150 \times e^{-\frac{(p_6 + (p_2 - 50))^2}{2 p_5^2}}$
* **$k_5$**: Generated via $-35 \times e^{-\frac{(p_8 + (p_1 - 25))^2}{2 p_7^2}}$

---

### 3. Normalization & QoS Parameters

In the CSV files (`data1.csv` through `data5.csv`), the data columns are organized according to:

* **Raw ICPs**
* **Raw KPIs**
* **`normalised_KPIs`**: KPIs transformed into utility values using z-score normalization.
* **`normalised_QoS_Threshold`**: Quality of Service thresholds applied to each KPI:
* **$q_1$**: $55$
* **$q_2$**: $95$
* **$q_3$**: $85$
* **$q_{41}$**: $75$
* **$q_{42}$**: $80$
* **$q_5$**: $-25$