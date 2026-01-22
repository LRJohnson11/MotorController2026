import numpy as np

Kt = .61 # NM/A_rms
Kv_no_load = 15.53 * 2 * np.pi / 60 #kv for no load in w/s
Kv_load = 12.05 * 2 *  np.pi / 60 #kv for nominal load w/s
Kv_peak = .68 * 2 * np.pi / 60 #kv for peak load w/s 
Ld = 96.5 * 10 ** -6 #96.5 uH
Lq = Ld # Lq ~ Ld
p = 10 #pole pairs
Tau = 130 # NM
R = 7.06 * 10 ** 3
flux = .03737
J = 0.02521 #kg/m^2
#winding configuration: star


Tau_max = 220 #Nm
S_max = 6500 #rpm
w_max = S_max * 2 * np.pi /60
w_e = w_max * 10