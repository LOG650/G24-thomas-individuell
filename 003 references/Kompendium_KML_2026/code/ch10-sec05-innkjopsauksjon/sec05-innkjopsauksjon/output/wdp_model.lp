\* WDP *\
Minimize
TotalCost: 4926000 x_B1 + 5484000 x_B2 + 3111000 x_B3 + 681600 x_B4
 + 13428800 x_B5 + 3739400 x_B6 + 2580000 x_E_L1_C1 + 2556000 x_E_L1_C2
 + 1720000 x_E_L1_C3 + 1852500 x_E_L1_C4 + 1580000 x_E_L2_C3
 + 1657500 x_E_L2_C4 + 2562000 x_E_L2_C5 + 1697500 x_E_L2_C6
 + 342000 x_E_L3_C7 + 378000 x_E_L3_C8 + 2748000 x_E_L4_C1 + 2682000 x_E_L4_C2
 + 1660000 x_E_L4_C3 + 1768000 x_E_L4_C4 + 2667000 x_E_L4_C5
 + 1743000 x_E_L4_C6 + 372000 x_E_L4_C7 + 409500 x_E_L4_C8
Subject To
Cover_C1: x_B1 + x_B5 + x_E_L1_C1 + x_E_L4_C1 = 1
Cover_C2: x_B1 + x_B5 + x_E_L1_C2 + x_E_L4_C2 = 1
Cover_C3: x_B2 + x_B3 + x_B5 + x_E_L1_C3 + x_E_L2_C3 + x_E_L4_C3 = 1
Cover_C4: x_B2 + x_B3 + x_B5 + x_B6 + x_E_L1_C4 + x_E_L2_C4 + x_E_L4_C4 = 1
Cover_C5: x_B2 + x_B5 + x_E_L2_C5 + x_E_L4_C5 = 1
Cover_C6: x_B5 + x_B6 + x_E_L2_C6 + x_E_L4_C6 = 1
Cover_C7: x_B4 + x_B5 + x_B6 + x_E_L3_C7 + x_E_L4_C7 = 1
Cover_C8: x_B4 + x_B5 + x_E_L3_C8 + x_E_L4_C8 = 1
Binaries
x_B1
x_B2
x_B3
x_B4
x_B5
x_B6
x_E_L1_C1
x_E_L1_C2
x_E_L1_C3
x_E_L1_C4
x_E_L2_C3
x_E_L2_C4
x_E_L2_C5
x_E_L2_C6
x_E_L3_C7
x_E_L3_C8
x_E_L4_C1
x_E_L4_C2
x_E_L4_C3
x_E_L4_C4
x_E_L4_C5
x_E_L4_C6
x_E_L4_C7
x_E_L4_C8
End
