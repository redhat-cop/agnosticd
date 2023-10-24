### KMM, NFD and Habana Gaudi Accelerators / GPU Setup Role ###

On the worker node :
sh-4.4# lspci -d : |grep -i Gaudi
10:1d.0 Processing accelerators: Habana Labs Ltd. HL-2000 AI Training Accelerator [Gaudi secured] (rev 01)
10:1e.0 Processing accelerators: Habana Labs Ltd. HL-2000 AI Training Accelerator [Gaudi secured] (rev 01)
20:1d.0 Processing accelerators: Habana Labs Ltd. HL-2000 AI Training Accelerator [Gaudi secured] (rev 01)
20:1e.0 Processing accelerators: Habana Labs Ltd. HL-2000 AI Training Accelerator [Gaudi secured] (rev 01)
90:1d.0 Processing accelerators: Habana Labs Ltd. HL-2000 AI Training Accelerator [Gaudi secured] (rev 01)
90:1e.0 Processing accelerators: Habana Labs Ltd. HL-2000 AI Training Accelerator [Gaudi secured] (rev 01)
a0:1d.0 Processing accelerators: Habana Labs Ltd. HL-2000 AI Training Accelerator [Gaudi secured] (rev 01)
a0:1e.0 Processing accelerators: Habana Labs Ltd. HL-2000 AI Training Accelerator [Gaudi secured] (rev 01)

sh-4.4# grep -E "$" /sys/class/habanalabs/hl?/*ver | cut -d / -f5-
hl0/armcp_kernel_ver:Linux OAM[0] gaudi 5.10.18-hl-gaudi-1.2.3-fw-32.6.6-sec-4 #1 SMP PREEMPT Wed Jan 4 20:45:04 IST 2023 aarch64 GNU/Linux
hl0/armcp_ver:armcpd version hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:47:16)
hl0/cpld_ver:0x0000001a
hl0/cpucp_kernel_ver:Linux OAM[0] gaudi 5.10.18-hl-gaudi-1.2.3-fw-32.6.6-sec-4 #1 SMP PREEMPT Wed Jan 4 20:45:04 IST 2023 aarch64 GNU/Linux
hl0/cpucp_ver:armcpd version hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:47:16)
hl0/driver_ver:1.10.0-416d95e
hl0/fuse_ver:00P1-HL2000A1-14-P64W99-07-00-07
hl0/infineon_ver:0x0b
hl0/preboot_btl_ver:BTL version 9f7a1057
hl0/preboot_btl_ver:Preboot version hl-gaudi-0.14.10-fw-32.0.13-sec-4 (Aug 13 2021 - 17:47:26)
hl0/thermal_ver:thermald version hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:48:02)
hl0/uboot_ver:U-Boot 2021.04-hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:43:58 +0200) build#: 6981
hl1/armcp_kernel_ver:Linux OAM[5] gaudi 5.10.18-hl-gaudi-1.2.3-fw-32.6.6-sec-4 #1 SMP PREEMPT Wed Jan 4 20:45:04 IST 2023 aarch64 GNU/Linux
hl1/armcp_ver:armcpd version hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:47:16)
hl1/cpld_ver:0x0000001a
hl1/cpucp_kernel_ver:Linux OAM[5] gaudi 5.10.18-hl-gaudi-1.2.3-fw-32.6.6-sec-4 #1 SMP PREEMPT Wed Jan 4 20:45:04 IST 2023 aarch64 GNU/Linux
hl1/cpucp_ver:armcpd version hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:47:16)
hl1/driver_ver:1.10.0-416d95e
hl1/fuse_ver:00P1-HL2000A1-14-P64W98-04-09-07
hl1/infineon_ver:0x0b
hl1/preboot_btl_ver:BTL version 9f7a1057
hl1/preboot_btl_ver:Preboot version hl-gaudi-0.14.10-fw-32.0.13-sec-4 (Aug 13 2021 - 17:47:26)
hl1/thermal_ver:thermald version hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:48:02)
hl1/uboot_ver:U-Boot 2021.04-hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:43:58 +0200) build#: 6981
hl2/armcp_kernel_ver:Linux OAM[1] gaudi 5.10.18-hl-gaudi-1.2.3-fw-32.6.6-sec-4 #1 SMP PREEMPT Wed Jan 4 20:45:04 IST 2023 aarch64 GNU/Linux
hl2/armcp_ver:armcpd version hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:47:16)
hl2/cpld_ver:0x0000001a
hl2/cpucp_kernel_ver:Linux OAM[1] gaudi 5.10.18-hl-gaudi-1.2.3-fw-32.6.6-sec-4 #1 SMP PREEMPT Wed Jan 4 20:45:04 IST 2023 aarch64 GNU/Linux
hl2/cpucp_ver:armcpd version hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:47:16)
hl2/driver_ver:1.10.0-416d95e
hl2/fuse_ver:00P1-HL2000A1-14-P64X03-14-06-06
hl2/infineon_ver:0x0b
hl2/preboot_btl_ver:BTL version 9f7a1057
hl2/preboot_btl_ver:Preboot version hl-gaudi-0.14.10-fw-32.0.13-sec-4 (Aug 13 2021 - 17:47:26)
hl2/thermal_ver:thermald version hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:48:02)
hl2/uboot_ver:U-Boot 2021.04-hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:43:58 +0200) build#: 6981
hl3/armcp_kernel_ver:Linux OAM[4] gaudi 5.10.18-hl-gaudi-1.2.3-fw-32.6.6-sec-4 #1 SMP PREEMPT Wed Jan 4 20:45:04 IST 2023 aarch64 GNU/Linux
hl3/armcp_ver:armcpd version hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:47:16)
hl3/cpld_ver:0x0000001a
hl3/cpucp_kernel_ver:Linux OAM[4] gaudi 5.10.18-hl-gaudi-1.2.3-fw-32.6.6-sec-4 #1 SMP PREEMPT Wed Jan 4 20:45:04 IST 2023 aarch64 GNU/Linux
hl3/cpucp_ver:armcpd version hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:47:16)
hl3/driver_ver:1.10.0-416d95e
hl3/fuse_ver:00P1-HL2000A1-14-P64X01-15-00-05
hl3/infineon_ver:0x0b
hl3/preboot_btl_ver:BTL version 9f7a1057
hl3/preboot_btl_ver:Preboot version hl-gaudi-0.14.10-fw-32.0.13-sec-4 (Aug 13 2021 - 17:47:26)
hl3/thermal_ver:thermald version hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:48:02)
hl3/uboot_ver:U-Boot 2021.04-hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:43:58 +0200) build#: 6981
hl4/armcp_kernel_ver:Linux OAM[2] gaudi 5.10.18-hl-gaudi-1.2.3-fw-32.6.6-sec-4 #1 SMP PREEMPT Wed Jan 4 20:45:04 IST 2023 aarch64 GNU/Linux
hl4/armcp_ver:armcpd version hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:47:16)
hl4/cpld_ver:0x0000001a
hl4/cpucp_kernel_ver:Linux OAM[2] gaudi 5.10.18-hl-gaudi-1.2.3-fw-32.6.6-sec-4 #1 SMP PREEMPT Wed Jan 4 20:45:04 IST 2023 aarch64 GNU/Linux
hl4/cpucp_ver:armcpd version hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:47:16)
hl4/driver_ver:1.10.0-416d95e
hl4/fuse_ver:00P1-HL2000A1-14-P64X78-04-03-06
hl4/infineon_ver:0x0b
hl4/preboot_btl_ver:BTL version 9f7a1057
hl4/preboot_btl_ver:Preboot version hl-gaudi-0.14.10-fw-32.0.13-sec-4 (Aug 13 2021 - 17:47:26)
hl4/thermal_ver:thermald version hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:48:02)
hl4/uboot_ver:U-Boot 2021.04-hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:43:58 +0200) build#: 6981
hl5/armcp_kernel_ver:Linux OAM[3] gaudi 5.10.18-hl-gaudi-1.2.3-fw-32.6.6-sec-4 #1 SMP PREEMPT Wed Jan 4 20:45:04 IST 2023 aarch64 GNU/Linux
hl5/armcp_ver:armcpd version hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:47:16)
hl5/cpld_ver:0x0000001a
hl5/cpucp_kernel_ver:Linux OAM[3] gaudi 5.10.18-hl-gaudi-1.2.3-fw-32.6.6-sec-4 #1 SMP PREEMPT Wed Jan 4 20:45:04 IST 2023 aarch64 GNU/Linux
hl5/cpucp_ver:armcpd version hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:47:16)
hl5/driver_ver:1.10.0-416d95e
hl5/fuse_ver:00P1-HL2000A1-14-P64X03-12-07-08
hl5/infineon_ver:0x0b
hl5/preboot_btl_ver:BTL version 9f7a1057
hl5/preboot_btl_ver:Preboot version hl-gaudi-0.14.10-fw-32.0.13-sec-4 (Aug 13 2021 - 17:47:26)
hl5/thermal_ver:thermald version hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:48:02)
hl5/uboot_ver:U-Boot 2021.04-hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:43:58 +0200) build#: 6981
hl6/armcp_kernel_ver:Linux OAM[6] gaudi 5.10.18-hl-gaudi-1.2.3-fw-32.6.6-sec-4 #1 SMP PREEMPT Wed Jan 4 20:45:04 IST 2023 aarch64 GNU/Linux
hl6/armcp_ver:armcpd version hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:47:16)
hl6/cpld_ver:0x0000001a
hl6/cpucp_kernel_ver:Linux OAM[6] gaudi 5.10.18-hl-gaudi-1.2.3-fw-32.6.6-sec-4 #1 SMP PREEMPT Wed Jan 4 20:45:04 IST 2023 aarch64 GNU/Linux
hl6/cpucp_ver:armcpd version hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:47:16)
hl6/driver_ver:1.10.0-416d95e
hl6/fuse_ver:00P1-HL2000A1-14-P64X01-11-05-10
hl6/infineon_ver:0x0b
hl6/preboot_btl_ver:BTL version 9f7a1057
hl6/preboot_btl_ver:Preboot version hl-gaudi-0.14.10-fw-32.0.13-sec-4 (Aug 13 2021 - 17:47:26)
hl6/thermal_ver:thermald version hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:48:02)
hl6/uboot_ver:U-Boot 2021.04-hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:43:58 +0200) build#: 6981
hl7/armcp_kernel_ver:Linux OAM[7] gaudi 5.10.18-hl-gaudi-1.2.3-fw-32.6.6-sec-4 #1 SMP PREEMPT Wed Jan 4 20:45:04 IST 2023 aarch64 GNU/Linux
hl7/armcp_ver:armcpd version hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:47:16)
hl7/cpld_ver:0x0000001a
hl7/cpucp_kernel_ver:Linux OAM[7] gaudi 5.10.18-hl-gaudi-1.2.3-fw-32.6.6-sec-4 #1 SMP PREEMPT Wed Jan 4 20:45:04 IST 2023 aarch64 GNU/Linux
hl7/cpucp_ver:armcpd version hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:47:16)
hl7/driver_ver:1.10.0-416d95e
hl7/fuse_ver:00P1-HL2000A1-14-P64X01-09-05-08
hl7/infineon_ver:0x0b
hl7/preboot_btl_ver:BTL version 9f7a1057
hl7/preboot_btl_ver:Preboot version hl-gaudi-0.14.10-fw-32.0.13-sec-4 (Aug 13 2021 - 17:47:26)
hl7/thermal_ver:thermald version hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:48:02)
hl7/uboot_ver:U-Boot 2021.04-hl-gaudi-1.2.3-fw-32.6.6-sec-4 (Jan 04 2023 - 20:43:58 +0200) build#: 6981

sh-4.4# lsmod |grep habana
habanalabs_en          57344  8
habanalabs           2207744  0


sh-4.4# dmesg | grep habana
[   69.849789] habanalabs: loading out-of-tree module taints kernel.
[   69.850698] habanalabs: module verification failed: signature and/or required key missing - tainting kernel
[   69.869035] habanalabs: loading driver, version: 1.10.0-416d95e
[   69.869410] habanalabs 0000:10:1d.0: habanalabs device found [1da3:1010] (rev 1)
[   69.869479] habanalabs 0000:10:1d.0: can't derive routing for PCI INT A
[   69.869481] habanalabs 0000:10:1d.0: PCI INT A: no GSI
[   69.869483] habanalabs 0000:90:1d.0: habanalabs device found [1da3:1010] (rev 1)
[   69.869561] habanalabs 0000:10:1e.0: habanalabs device found [1da3:1010] (rev 1)
[   69.869585] habanalabs 0000:90:1d.0: can't derive routing for PCI INT A
[   69.869588] habanalabs 0000:90:1d.0: PCI INT A: no GSI
[   69.869595] habanalabs 0000:10:1e.0: can't derive routing for PCI INT A
[   69.869597] habanalabs 0000:10:1e.0: PCI INT A: no GSI
[   69.869698] habanalabs 0000:90:1e.0: habanalabs device found [1da3:1010] (rev 1)
[   69.869711] habanalabs 0000:20:1d.0: habanalabs device found [1da3:1010] (rev 1)
[   69.869750] habanalabs 0000:20:1d.0: can't derive routing for PCI INT A
[   69.869751] habanalabs 0000:20:1d.0: PCI INT A: no GSI
[   69.869758] habanalabs 0000:90:1e.0: can't derive routing for PCI INT A
[   69.869760] habanalabs 0000:90:1e.0: PCI INT A: no GSI
[   69.869923] habanalabs 0000:20:1e.0: habanalabs device found [1da3:1010] (rev 1)
[   69.869957] habanalabs 0000:20:1e.0: can't derive routing for PCI INT A
[   69.869958] habanalabs 0000:20:1e.0: PCI INT A: no GSI
[   69.869958] habanalabs 0000:a0:1d.0: habanalabs device found [1da3:1010] (rev 1)
[   69.870037] habanalabs 0000:a0:1d.0: can't derive routing for PCI INT A
[   69.870039] habanalabs 0000:a0:1d.0: PCI INT A: no GSI
[   69.870146] habanalabs 0000:a0:1e.0: habanalabs device found [1da3:1010] (rev 1)
[   69.870177] habanalabs 0000:a0:1e.0: can't derive routing for PCI INT A
[   69.870179] habanalabs 0000:a0:1e.0: PCI INT A: no GSI
[   69.891868] habanalabs hl1: Loading secured firmware to device, may take some time...
[   69.913710] habanalabs hl2: Loading secured firmware to device, may take some time...
[   69.920954] habanalabs hl4: Loading secured firmware to device, may take some time...
[   69.921945] habanalabs hl6: Loading secured firmware to device, may take some time...
[   69.928162] habanalabs hl0: Loading secured firmware to device, may take some time...
[   69.929564] habanalabs hl3: Loading secured firmware to device, may take some time...
[   69.946702] habanalabs hl5: Loading secured firmware to device, may take some time...
[   69.948599] habanalabs hl7: Loading secured firmware to device, may take some time...
[   70.004300] habanalabs hl2: preboot full version: 'Preboot version hl-gaudi-0.14.10-fw-32.0.13-sec-4 (Aug 13 2021 - 17:47:26)'
[   70.004304] habanalabs hl2: BTL version 9f7a1057
[   70.009464] habanalabs hl1: preboot full version: 'Preboot version hl-gaudi-0.14.10-fw-32.0.13-sec-4 (Aug 13 2021 - 17:47:26)'
[   70.009469] habanalabs hl1: BTL version 9f7a1057
[   70.086534] habanalabs hl4: preboot full version: 'Preboot version hl-gaudi-0.14.10-fw-32.0.13-sec-4 (Aug 13 2021 - 17:47:26)'
[   70.086537] habanalabs hl4: BTL version 9f7a1057
[   70.101840] habanalabs hl3: preboot full version: 'Preboot version hl-gaudi-0.14.10-fw-32.0.13-sec-4 (Aug 13 2021 - 17:47:26)'
[   70.101844] habanalabs hl3: BTL version 9f7a1057
[   70.168501] habanalabs hl0: preboot full version: 'Preboot version hl-gaudi-0.14.10-fw-32.0.13-sec-4 (Aug 13 2021 - 17:47:26)'
[   70.168504] habanalabs hl0: BTL version 9f7a1057
[   70.184054] habanalabs hl6: preboot full version: 'Preboot version hl-gaudi-0.14.10-fw-32.0.13-sec-4 (Aug 13 2021 - 17:47:26)'
[   70.184059] habanalabs hl6: BTL version 9f7a1057
[   70.264781] habanalabs hl5: preboot full version: 'Preboot version hl-gaudi-0.14.10-fw-32.0.13-sec-4 (Aug 13 2021 - 17:47:26)'
[   70.264785] habanalabs hl5: BTL version 9f7a1057
[   70.276628] habanalabs hl7: preboot full version: 'Preboot version hl-gaudi-0.14.10-fw-32.0.13-sec-4 (Aug 13 2021 - 17:47:26)'
[   70.276632] habanalabs hl7: BTL version 9f7a1057
[   79.231837] habanalabs hl1: boot-fit version 32.6.6-sec-4
[   79.352467] habanalabs hl0: boot-fit version 32.6.6-sec-4
[   79.358382] habanalabs hl5: boot-fit version 32.6.6-sec-4
[   79.363470] habanalabs hl4: boot-fit version 32.6.6-sec-4
[   79.368358] habanalabs hl2: boot-fit version 32.6.6-sec-4
[   79.376242] habanalabs hl6: boot-fit version 32.6.6-sec-4
[   79.381249] habanalabs hl7: boot-fit version 32.6.6-sec-4
[   79.385614] habanalabs hl3: boot-fit version 32.6.6-sec-4
[   80.742144] habanalabs hl5: Successfully loaded firmware to device
[   80.744078] habanalabs hl4: Successfully loaded firmware to device
[   80.745561] habanalabs hl0: Successfully loaded firmware to device
[   80.746480] habanalabs hl1: Successfully loaded firmware to device
[   80.756913] habanalabs hl2: Successfully loaded firmware to device
[   80.765893] habanalabs hl7: Successfully loaded firmware to device
[   80.767465] habanalabs hl3: Successfully loaded firmware to device
[   80.768930] habanalabs hl6: Successfully loaded firmware to device
[   83.311953] habanalabs hl1: Linux version 32.6.6-sec-4
[   83.335937] habanalabs hl0: Linux version 32.6.6-sec-4
[   83.349937] habanalabs hl6: Linux version 32.6.6-sec-4
[   83.351928] habanalabs hl7: Linux version 32.6.6-sec-4
[   83.371929] habanalabs hl5: Linux version 32.6.6-sec-4
[   83.375929] habanalabs hl2: Linux version 32.6.6-sec-4
[   83.378927] habanalabs hl3: Linux version 32.6.6-sec-4
[   83.378932] habanalabs hl4: Linux version 32.6.6-sec-4
[   83.405947] habanalabs hl1: Found GAUDI SEC device with 32GB DRAM
[   83.444930] habanalabs hl0: Found GAUDI SEC device with 32GB DRAM
[   83.445926] habanalabs hl6: Found GAUDI SEC device with 32GB DRAM
[   83.456918] habanalabs hl7: Found GAUDI SEC device with 32GB DRAM
[   83.466937] habanalabs hl5: Found GAUDI SEC device with 32GB DRAM
[   83.482010] habanalabs hl4: Found GAUDI SEC device with 32GB DRAM
[   83.486010] habanalabs hl2: Found GAUDI SEC device with 32GB DRAM
[   83.486917] habanalabs hl3: Found GAUDI SEC device with 32GB DRAM
[   84.637541] habanalabs hl1: hwmon0: add sensors information
[   84.637545] habanalabs hl1: Successfully added device 0000:90:1d.0 to habanalabs driver
[   84.657508] habanalabs hl7: hwmon1: add sensors information
[   84.657515] habanalabs hl7: Successfully added device 0000:a0:1e.0 to habanalabs driver
[   84.676582] habanalabs hl0: hwmon2: add sensors information
[   84.676588] habanalabs hl0: Successfully added device 0000:10:1d.0 to habanalabs driver
[   84.683519] habanalabs hl2: hwmon3: add sensors information
[   84.683525] habanalabs hl2: Successfully added device 0000:10:1e.0 to habanalabs driver
[   84.685193] habanalabs hl6: hwmon4: add sensors information
[   84.685196] habanalabs hl6: Successfully added device 0000:a0:1d.0 to habanalabs driver
[   84.694376] habanalabs hl5: hwmon5: add sensors information
[   84.694379] habanalabs hl5: Successfully added device 0000:20:1e.0 to habanalabs driver
[   84.721371] habanalabs hl4: hwmon6: add sensors information
[   84.721373] habanalabs hl4: Successfully added device 0000:20:1d.0 to habanalabs driver
[   84.724540] habanalabs hl3: hwmon7: add sensors information
[   84.724543] habanalabs hl3: Successfully added device 0000:90:1e.0 to habanalabs driver
[   84.800115] habanalabs_en: loading driver, version: 1.10.0-416d95e

