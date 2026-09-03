# Schex, Cremer, Dettmar - Connectionless Bluetooth Channel Sounding via PAwR (arXiv:2605.17094v2) - excerpts

Source: https://arxiv.org/abs/2605.17094 / https://arxiv.org/html/2605.17094v2
Submitted 2026-05-16, v2 2026-08-04. Fetched: 2026-09-03

## Abstract
```
 Abstract: Bluetooth Core Specification v6.0 introduces Channel Sounding (CS) as a high-accuracy ranging primitive for Bluetooth Low Energy. However, the standard procedure requires per-pair connections. This binds ranging to a multi-stage initiation procedure, limits concurrent partners per radio, and forces result transfer over the connection. We present a connectionless CS architecture combining the LE CS Test command with Periodic Advertising with Responses (PAwR). A Central Orchestrator, a gateway, and synchronized CS devices handle coordination, configuration alignment, and result aggregation at the application layer. Each device derives its role, deterministic random bit generator initialization state, channel sequence, and response slot assignment from its device index and a Peer-to-Peer Assignment Matrix. The deterministic channel sequence prevents same-step collisions across parallel CS procedures, and the matrix can be updated per cycle to reconfigure arbitrary device-to-device pairings within a PAwR subevent group. A compact data plane omits fields recoverable from the shared measurement configuration and reduces the ranging-data payload by approximately 69%, so complete results are reported through PAwR response slots. A proof-of-concept evaluation on the nRF54L15 platform shows that deterministic channel management eliminates the collision-induced outliers observed under simulated dense-deployment channel overlaps. At a 1 s update cycle, the architecture reduces steady-state active charge by 40-48% relative to a fair connected baseline, cuts per-switch initiation overhead by approximately 98%, and, under per-cycle partner switching, achieves up to 88% lower total charge over 24 h. An empirical timing model projects up to 14,080 active devices per PAwR train for a four-measurement workload.
 Comments: 
```

## Prototype platform, accuracy Table I, energy Tables II-V, battery lifetime
```
 IV-A 1 Prototype Platform 
 The prototype comprises eight identical custom CS devices based on the Ezurio BL54L15 module, which integrates the Nordic Semiconductor nRF54L15 SoC with native support for both CS and PAwR. Each device is powered by a CR2032 coin cell (3 V, 240 mAh) and equipped with a dedicated 32.768 kHz Low-Frequency Crystal Oscillator (LFXO) that serves as the clock source for the Global Real-Time Counter (GRTC) system timer, enabling low-power timekeeping with the tickless kernel. The firmware is built on the nRF Connect SDK v3.1.0 (Zephyr RTOS) with the Nordic SoftDevice Controller. An nRF54L15 Development Kit serves as the GW, connected to the CO via a UART-to-USB link. The CO runs a Python-based multi-threaded pipeline for configuration generation, data aggregation, and distance estimation. A prototype platform overview is shown in Fig.   3 . 
     (a) Top view (b) Bottom view    
 Fig. 3: Custom CS device based on the Ezurio BL54L15 module: (a) top view with SoC module, LFXO, and supporting peripherals; (b) bottom view with the CR2032 coin cell in its holder. 
 IV-A 2 Configurations 
 Unless stated otherwise, each CS procedure consists of one CS subevent with 3 mode-0 steps followed by either 72 mode-2 steps (1 MHz spacing) or 37 mode-2 steps (2 MHz spacing). We refer to these baseline scenarios as 1 × \times 72 ch. and 1 × \times 37 ch., where the leading factor denotes the number of CS procedures executed per update cycle. CS TX power is set to + 8 +8  dBm across all experiments to achieve the highest possible SNR, while general BLE data transmission uses the default 0 dBm. The update cycle is 1 s unless stated otherwise. Experiment-specific parameters (e.g., number of measurements per cycle) are given in the respective subsections. Table   V in the Appendix lists the complete configuration for reproducibility. 
 IV-A 3 Processing Pipeline (Proof-of-Concept) 
 Distance estimation uses a proof-of-concept pipeline based on the Inverse Fast Fourier Transform (IFFT). For each CS procedure, the Initiator and Reflector PCTs are combined via complex multiplication to cancel the unknown local oscillator starting phases  [ 2 ] . Spectral gaps at channels excluded from the CS channel set (e.g., primary advertising channels) are filled with linear interpolation, and the resulting frequency-domain vector is zero-padded before applying an IFFT to obtain the Channel Impulse Response (CIR). The dominant peak in the CIR magnitude is detected and converted to a distance estimate based on the speed of light and system parameters. A static calibration offset is subtracted to compensate for hardware-related delays (e.g., antenna group delay). This estimator is intentionally simple and is used to confirm measurability and to quantify the impact of collision stress. It is not presented as an accuracy benchmark. Advanced estimators and multipath/non-line-of-sight optimization are out of scope. 
 IV-A 4 Metrics 
 We report Mean Absolute Error (MAE), peak error, 90th-percentile error ( P 90 P_{90} ), and Standard Deviation (STD) to characterize the proof-of-concept distance estimates. 
 IV-B Channel Collision Robustness in Dense Deployments 
 IV-B 1 Setup 
 Measurements were performed in an open field with a grass surface to minimize multipath reflections. All eight CS device prototypes were mounted pairwise on two tripods (see Fig.   4 ). Devices within each pair were aligned parallel for consistent antenna polarization. 
 Device pairs 0 ↔ \leftrightarrow 1 and 2 ↔ \leftrightarrow 3 operated under the proposed system with collision-free channel assignments (upper mounts). Pairs 4 ↔ \leftrightarrow 5 and 6 ↔ \leftrightarrow 7 simulated collision-stress operation via fixed channel overlaps (lower mounts, see Sec.  IV-B2 ). To limit temporal variation in the experimental conditions, both scenarios were executed within the same update cycle and anchored to the same PAwR subevent. The collision-free pairs first executed four consecutive CS procedures in parallel, immediately followed by the collision-stress pairs executing the same sequence. Distances ranged from 0.5 m to 5.5 m in 0.5 m increments, measured with a laser distance meter. A total of 120 measurements per distance per pair were collected. The collision-free pairs also served as calibration reference: the static offset subtracted by the distance estimator (see Sec.  IV-A3 ) was determined as the mean error of the uncorrected estimates over these two pairs, yielding an offset of 1.24 m. 
 Since the deterministic channel management of the proposed architecture (see Sec.  III-D ) prevents channel overlaps by design, the collision-free results with two simultaneously measuring pairs represent the expected behavior with respect to same-step channel collisions for up to 72 simultaneous pairs. Aggregate effects of many concurrent transmitters (e.g., adjacent-channel interference) are not captured by this setup. 
 (a) (b) 
 Fig. 4: Distance measurement setup. (a) Eight CS devices form four ranging pairs (0 ↔ \leftrightarrow 1, 2 ↔ \leftrightarrow 3, 4 ↔ \leftrightarrow 5, 6 ↔ \leftrightarrow 7) across two tripods. The two devices of each pair sit on opposite tripods, separated by the measured range (varied over 0.5–5.5 m). The collision-free pairs (0 ↔ \leftrightarrow 1, 2 ↔ \leftrightarrow 3) share the upper mount (156 cm height), and the collision-stress pairs (4 ↔ \leftrightarrow 5, 6 ↔ \leftrightarrow 7) the lower mount (140 cm height). On each mount, the two pairs are offset 41 cm horizontally. (b) GW (nRF54L15 Development Kit on tripod) and CO (laptop). 
 IV-B 2 Interference-Collision Model 
 In standard CS operation, each Initiator-Reflector pair uses a randomized channel sequence. When P P pairs measure simultaneously over N N channels, the per-step collision probability p p (i.e., the probability that at least one of the other P − 1 P-1 pairs uses the same channel) is 
 p = 1 − ( N − 1 N ) P − 1 . p=1-\left(\frac{N-1}{N}\right)^{P-1}. 
 (5) 
 By linearity of expectation, the expected number of overlapping steps across the N N channels of one CS procedure is 
 E ⁡ [ X ] = N ⋅ [ 1 − ( N − 1 N ) P − 1 ] . \mathrm{E}[X]=N\cdot\left[1-\left(\frac{N-1}{N}\right)^{P-1}\right]. 
 (6) 
 Preliminary tests showed that overlap counts beyond approximately 24 caused some CS procedures to fail entirely. We therefore chose P = 30 P=30 simultaneous pairs with N = 72 N=72 channels, for which  ( 6 ) yields E ⁡ [ X ] ≈ 24 \mathrm{E}[X]\approx 24 overlapping channels per procedure, representing the highest collision load that still permits reliable CS execution. 
 To stress collision robustness without requiring 30 physical pairs, the collision-stress baseline pairs (4 ↔ \leftrightarrow 5, 6 ↔ \leftrightarrow 7) ran the proposed system firmware with its deterministic channel management overridden by a channel sequence containing 24 randomly positioned overlaps, matching the expected collision count for P = 30 P=30 . 
 IV-B 3 Results and Analysis 
 Fig.   5 and Table   I summarize the proof-of-concept results for 1 MHz channel spacing (72 channels). The collision-free pairs serve as the stable baseline. Under collision stress, peak errors increase from 25 cm to over 300 cm and STD more than doubles. 
 These results confirm that deterministic channel management effectively eliminates collision-induced outliers and yields stable, evaluable measurements even with multiple pairs measuring simultaneously. Since both channel spacing configurations occupy the same total bandwidth and exhibited no significant differences in this low-multipath environment, we report only the 1 MHz results. 
 (a) Collision-free (b) Collision-stress 
 Fig. 5: Estimated vs. real distance for 1 MHz channel spacing (72 channels, 120 measurements per distance per pair). Solid lines denote the per-pair mean, shaded bands the min–max range, and the dashed line the ideal y = x y=x . (a) Collision-free operation (pairs 0 ↔ \leftrightarrow 1, 2 ↔ \leftrightarrow 3): the min–max band is so narrow that it is barely visible. (b) Operation with simulated channel collisions (pairs 4 ↔ \leftrightarrow 5, 6 ↔ \leftrightarrow 7, 24 overlapping channels): substantially wider band with large outliers. 
 TABLE I: Proof-of-concept ranging performance with and without simulated channel collisions (1 MHz channel spacing, 72 channels, 120 measurements per distance per pair). 
 Scenario 
 Error (cm) 
 MAE 
 Peak 
 𝑷 𝟗𝟎 \boldsymbol{P_{90}} 
 STD 
 Collision-free (0 ↔ \leftrightarrow 1) 
 10 
 25 
 20 
 12 
 Collision-free (2 ↔ \leftrightarrow 3) 
 6 
 25 
 16 
 9 
 Collision-stress (4 ↔ \leftrightarrow 5) 
 14 
 331 
 27 
 29 
 Collision-stress (6 ↔ \leftrightarrow 7) 
 13 
 309 
 28 
 20 
 IV-C Energy Efficiency 
 IV-C 1 Setup 
...
 3 
 IV-C 4 Steady-State Comparison 
 To isolate the architectural differences between both approaches, we define the steady-state active charge per update cycle by excluding the sleep contribution Q sleep = 3 ​ μ ​ C Q_{\mathrm{sleep}}=3\,\mu\mathrm{C} , which is identical across configurations (see Tables   II and  III ), and include Q sync = 1 ​ μ ​ C Q_{\mathrm{sync}}=1\,\mu\mathrm{C} as a fixed per-cycle overhead for the proposed approach. 
 For the connected baseline, the steady-state active charge for a single measurement is 
 Q std , ss = Q cs + Q data , std + Q conn . Q_{\mathrm{std,ss}}=Q_{\mathrm{cs}}+Q_{\mathrm{data,std}}+Q_{\mathrm{conn}}. 
 (8) 
 For the proposed connectionless approach, 
 Q prop , ss = Q sync + Q cs + Q data , prop , Q_{\mathrm{prop,ss}}=Q_{\mathrm{sync}}+Q_{\mathrm{cs}}+Q_{\mathrm{data,prop}}, 
 (9) 
 where Q cs Q_{\mathrm{cs}} , Q data , std Q_{\mathrm{data,std}} , and Q conn Q_{\mathrm{conn}} are the CS , Data TX , and Conn. events charge contributions listed in Table   II , and Q data , prop Q_{\mathrm{data,prop}} is the Data TX contribution listed in Table   III . In the latter, Data TX refers to a PAwR response slot transmission rather than a connection event carrying a Ranging Data segment. 
 Using the values in Tables   II (at CI = 166.25 ​ ms \mathrm{CI}=166.25\,\mathrm{ms} ) and  III , the proposed approach reduces steady-state active charge from Q std , ss = 103 ​ μ ​ C Q_{\mathrm{std,ss}}=103\,\mu\mathrm{C} to Q prop , ss = 62 ​ μ ​ C Q_{\mathrm{prop,ss}}=62\,\mu\mathrm{C} for 72 channels ( 40 % reduction ), and from Q std , ss = 67 ​ μ ​ C Q_{\mathrm{std,ss}}=67\,\mu\mathrm{C} to Q prop , ss = 35 ​ μ ​ C Q_{\mathrm{prop,ss}}=35\,\mu\mathrm{C} for 37 channels ( 48 % reduction ). 
 The savings stem from two factors. First, the compact payload serialization described in Sec.  III-E reduces Data TX charge by 78 % (72 ch.) and 73 % (37 ch.), contributing 61 % and 34 % of the respective total savings. Second, elimination of periodic connection events contributes 39 % (72 ch.) and 66 % (37 ch.) of the savings. The CS procedure charge is identical in both approaches, as the air-interface procedure is unchanged. 
 For a device performing N meas N_{\mathrm{meas}} measurements per update cycle, the connected baseline charge scales as N meas ​ ( Q cs + Q data , std + Q conn ) N_{\mathrm{meas}}(Q_{\mathrm{cs}}+Q_{\mathrm{data,std}}+Q_{\mathrm{conn}}) , since each peer requires its own LE ACL connection. The proposed approach amortizes a single PAwR synchronization over all measurements, scaling as Q sync + N meas ​ ( Q cs + Q data , prop ) Q_{\mathrm{sync}}+N_{\mathrm{meas}}(Q_{\mathrm{cs}}+Q_{\mathrm{data,prop}}) . For N meas = 4 N_{\mathrm{meas}}=4 measurements to four fixed peers (e.g., four anchors in a conventional localization deployment) at 37 channels and CI = 166.25 ​ ms \mathrm{CI}=166.25\,\mathrm{ms} , this gives 268 ​ μ ​ C 268\,\mu\mathrm{C} versus 137 ​ μ ​ C 137\,\mu\mathrm{C} , a 49 % reduction . 
 IV-C 5 Initiation Overhead and Partner Switching 
 In connection-based operation, each partner switch requires tearing down the existing LE ACL connection, establishing a new one, and repeating the full initiation procedure, all of which incur substantial overhead. By contrast, the proposed architecture treats partner switching as a measurement configuration update distributed via PAwR. In dense deployments (see Sec.  I ), partner switching and multi-peer scheduling become frequent, making this overhead a dominant factor for connection-based approaches. 
 Table   IV summarizes the measured initiation overhead for three CIs. In each case, 53 connection events were required from connection start to the first CS procedure. Increasing the CI substantially increases time-to-first-measurement. 
 TABLE IV: Measured initiation overhead from connection start to first CS procedure (53 connection events). 
 Conn. interval (ms) 
 Time to first CS (s) 
 Charge ( μ \boldsymbol{\mu} C) 
 18.75 
 0.99 
 163 
 50.00 
 2.65 
 176 
 166.25 
 8.81 
 200 
 Comparing per-switch overhead, the proposed approach requires only Q cfg = 3 ​ μ ​ C Q_{\mathrm{cfg}}=3\,\mu\mathrm{C} (see Table   III ) for receiving and processing a new measurement configuration, representing a reduction of approximately 98 % relative to the connection-based initiation charge Q init Q_{\mathrm{init}} (see Table   IV ) across all three CIs. Relative to the steady-state reception of the periodic PAwR indication, a partner switch adds only the incremental cost of Δ ​ Q reconf = Q cfg − Q sync = 2 ​ μ ​ C \Delta Q_{\mathrm{reconf}}=Q_{\mathrm{cfg}}-Q_{\mathrm{sync}}=2\,\mu\mathrm{C} for the full configuration payload reception. 
 To compare both approaches over an extended time horizon T hor T_{\mathrm{hor}} for a device performing N meas N_{\mathrm{meas}} measurements per update cycle, we model the total consumed charge as 
 Q std , tot \displaystyle Q_{\mathrm{std,tot}} 
 = N cyc ​ [ N meas ​ ( Q cs + Q data , std + Q conn ) + Q sleep ] \displaystyle=N_{\mathrm{cyc}}\!\bigl[N_{\mathrm{meas}}(Q_{\mathrm{cs}}\!+\!Q_{\mathrm{data,std}}\!+\!Q_{\mathrm{conn}})+Q_{\mathrm{sleep}}\bigr] 
 + N sw ​ Q init , \displaystyle\quad+N_{\mathrm{sw}}\,Q_{\mathrm{init}}, 
 (10) 
 Q prop , tot \displaystyle Q_{\mathrm{prop,tot}} 
 = N cyc ​ [ Q sync + N meas ​ ( Q cs + Q data , prop ) + Q sleep ] \displaystyle=N_{\mathrm{cyc}}\!\bigl[Q_{\mathrm{sync}}\!+\!N_{\mathrm{meas}}(Q_{\mathrm{cs}}\!+\!Q_{\mathrm{data,prop}})+Q_{\mathrm{sleep}}\bigr] 
 + N sw ​ Δ ​ Q reconf , \displaystyle\quad+N_{\mathrm{sw}}\,\Delta Q_{\mathrm{reconf}}, 
 (11) 
 where N cyc = T hor / T upd N_{\mathrm{cyc}}=T_{\mathrm{hor}}/T_{\mathrm{upd}} is the number of update cycles, N sw N_{\mathrm{sw}} is the number of partner switches, and Q sleep = I sleep ⋅ T upd Q_{\mathrm{sleep}}=\mbox{$I_{\mathrm{sleep}}\cdot T_{\mathrm{upd}}$} is the sleep charge per cycle ( 3 ​ μ ​ C 3\,\mu\mathrm{C} for T upd = 1 ​ s T_{\mathrm{upd}}=1\,\mathrm{s} ). For the standard approach, both Q conn Q_{\mathrm{conn}} (see Table   II ) and Q init Q_{\mathrm{init}} (see Table   IV ) must correspond to the same CI, which must be short enough for initiation to complete within the available time between switches. 
 Table   V illustrates this model over T hor = 24 ​ h T_{\mathrm{hor}}=24\,\mathrm{h} for N meas = 1 N_{\mathrm{meas}}=1 measurement with 37 channels and T upd = 1 ​ s T_{\mathrm{upd}}=1\,\mathrm{s} ( N cyc = 86,400 N_{\mathrm{cyc}}=86{,}400 ). The comparison uses N meas = 1 N_{\mathrm{meas}}=1 because the frequent switching scenario requires CI = 18.75 ​ ms \mathrm{CI}=18.75\,\mathrm{ms} for initiation to complete within 1 s. At this short interval, frequent initiation and CS procedures must be interleaved with the connection events of multiple LE ACL connections  [ 1 ] . Maintaining these competing link-layer activities on a single radio places severe scheduling demands on the Bluetooth Controller. 
 For moderate switching (every 10 s), CI = 166.25 ​ ms \mathrm{CI}=166.25\,\mathrm{ms} is used because the initiation time of 8.81 s fits within the 10 s switching period, yielding the lowest per-cycle charge. 
 TABLE V: Consumed charge over T hor = 24 ​ h T_{\mathrm{hor}}=24\,\mathrm{h} for N meas = 1 N_{\mathrm{meas}}=1 measurement (37 channels, T upd = 1 ​ s T_{\mathrm{upd}}=1\,\mathrm{s} ), computed via  ( 10 ) and  ( 11 ) . 
 Scenario 
 𝑵 𝐬𝐰 \boldsymbol{N_{\mathrm{sw}}} 
 Charge (mC) 
 Reduction 
 Standard 
 Proposed 
 No switching 
 0 
 6,048 
 3,283 
 46 % 
 Moderate (every 10 s) 
 8,640 
 7,776 
 3,300 
 58 % 
 Frequent (every cycle) 
 86,400 
 28,598 
 3,456 
 88 % 
 As switching frequency increases, initiation overhead increasingly dominates the standard approach. With moderate switching (every 10 s), the proposed system already achieves a 58 % charge reduction . Under per-cycle switching, the standard system must additionally use CI = 18.75 ​ ms \mathrm{CI}=18.75\,\mathrm{ms} , which raises Q conn Q_{\mathrm{conn}} from 22 22 to 120 ​ μ ​ C 120\,\mu\mathrm{C} per cycle, compounding the overhead and resulting in a reduction of 88 % : the proposed system consumes approximately an order of magnitude less charge. 
 IV-C 6 Battery Lifetime Estimation 
 To translate these charge savings into practical device lifetime for the proposed connectionless system, the expected operational duration is estimated for a nominal CR2032 coin cell capacity of 240 mAh at 3 V. The average current over an update interval T upd T_{\mathrm{upd}} is 
 I ¯ = Q active T upd + I sleep , \bar{I}=\frac{Q_{\mathrm{active}}}{T_{\mathrm{upd}}}+I_{\mathrm{sleep}}, 
 (12) 
 where Q active Q_{\mathrm{active}} is the total active charge per cycle of the considered configuration. For the proposed system, this comprises Q sync Q_{\mathrm{sync}} in steady state, or Q cfg Q_{\mathrm{cfg}} in cycles that carry a configuration update, plus the charges for CS and Data TX . For the lifetime estimate, a datasheet-based sleep current of I sleep = 2.9 ​ μ ​ A I_{\mathrm{sleep}}=2.9\,\mu\mathrm{A} is assumed for the Sleep Configuration listed in Table   V   [ 19 ] . This corresponds to Q sleep ≈ 3 ​ μ ​ C Q_{\mathrm{sleep}}\approx 3\,\mu\mathrm{C} for T upd = 1 ​ s T_{\mathrm{upd}}=1\,\mathrm{s} , as reflected in Tables   II and  III . For longer T upd T_{\mathrm{upd}} , the sleep charge per cycle increases as I sleep ​ T upd I_{\mathrm{sleep}}T_{\mathrm{upd}} , whereas the active charge is amortized over a longer interval. Accordingly, the average-current model in  ( 12 ) retains an approximately constant sleep-current term I sleep I_{\mathrm{sleep}} . Expected lifetime (in days) for a battery with capacity C C (mAh) is 
 L = 1000 ​ C 24 ​ I ¯ , L=\frac{1000\,C}{24\,\bar{I}}, 
 (13) 
 where I ¯ \bar{I} is expressed in μ ​ A \mu\mathrm{A} . 
 As a practical dynamic scenario for the proposed system, consider a device performing four CS measurements per cycle to four peers with 37 channels at a CS TX power of 0 dBm. Relative to the measured + 8 ​ dBm +8\,\mathrm{dBm} case, the CS procedure charge at 0 ​ dBm 0\,\mathrm{dBm} is assumed to be approximately halved based on the lower TX current  [ 19 ] . Assuming one measurement configuration update per cycle, the resulting active charge is approximated as Q active ≈ Q cfg + 4 ​ ( Q cs , 0 ​ dBm + Q data , prop ) ≈ 79 ​ μ ​ C Q_{\mathrm{active}}\approx Q_{\mathrm{cfg}}+4\,(Q_{\mathrm{cs},0\,\mathrm{dBm}}+Q_{\mathrm{data,prop}})\approx 79\,\mu\mathrm{C} per cycle. With T upd = 1 ​ s T_{\mathrm{upd}}=1\,\mathrm{s} , the estimated lifetime is approximately 4 months ; at T upd = 30 ​ s T_{\mathrm{upd}}=30\,\mathrm{s} , it extends to approximately 5 years , confirming suitability for long-term, battery-powered localization. 
 IV-D System Scalability and Capacity 
 IV-D 1 Timing Model 
 Within one PAwR subevent, an active device receives the AUX_SYNC_SUBEVENT_IND PDU, executes its configured CS procedures, processes the resulting data, and transmits one or more AUX_SYNC_SUBEVENT_RSP PDUs in the response slot window. Fig.   8 shows the measured current profile annotated with the corresponding timing phases for the 4 × \times 37-channel configuration. 
 Fig. 8: Measured subevent timing phases for N meas = 4 N_{\mathrm{meas}}=4 CS procedures over 37 channels (2 MHz spacing). T rx T_{\mathrm{rx}} is the duration from the start of the AUX_SYNC_SUBEVENT_IND reception to the start of the first CS procedure, T cs T_{\mathrm{cs}} is the duration of one CS procedure, T dp T_{\mathrm{dp}} is the data-processing delay between the last CS procedure and the start of the response slot window, T tx , win T_{\mathrm{tx,win}} is the response slot window, T pre T_{\mathrm{pre}} is the pre-transmission phase (reception, measurements, and data processing), which equals the configured response slot delay, and T sub T_{\mathrm{sub}} is the full subevent. The two response bursts within T tx , win T_{\mathrm{tx,win}} correspond to N rsp = 2 N_{\mathrm{rsp}}=2 response PDUs. The open right brackets indicate that T tx , win T_{\mathrm{tx,win}} and T sub T_{\mathrm{sub}} extend beyond the visible window. The small unlabeled current peak immediately preceding T rx T_{\mathrm{rx}} is the wake-up from sleep and radio ramp-up that prepares the receiver for the scheduled IND PDU. 
 The pre-transmission duration is the sum of the three preceding phases, 
 T pre = T rx + N meas ​ T cs + T dp , T_{\mathrm{pre}}=T_{\mathrm{rx}}+N_{\mathrm{meas}}\,T_{\mathrm{cs}}+T_{\mathrm{dp}}, 
 (14) 
 where T rx T_{\mathrm{rx}} is the duration from the start of the AUX_SYNC_SUBEVENT_IND reception to the start of the first CS procedure, T cs T_{\mathrm{cs}} is the duration of one CS procedure, T dp T_{\mathrm{dp}} is the data-processing delay between the last CS procedure and the start of the response slot window, and N meas N_{\mathrm{meas}} is the number of CS procedures per device per update cycle. In PAwR terms, T pre T_{\mathrm{pre}} corresponds to the response slot delay, i.e., the configured offset (an integer multiple of 1.25 ms) between the start of the AUX_SYNC_SUBEVENT_IND PDU and the first response slot  [ 1 ] . The prototype configures 61.25 ms for the 4 × \times 72-channel and 41.25 ms for the 4 × \times 37-channel configuration. The response slot window aggregates N rs N_{\mathrm{rs}} slots of spacing T rs T_{\mathrm{rs}} (see Sec.  III-D , Sec.  III-E ), 
 T tx , win = N rs ​ T rs , T_{\mathrm{tx,win}}=N_{\mathrm{rs}}\,T_{\mathrm{rs}}, 
```
