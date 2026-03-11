% demonstrate reading and plotting THEMIS video

fn = "../src/themisasi/tests/thg_l1_asf_fykn_2006093004_v01.cdf";

[data, t, hdrs, site] = readTHEMIS(fn);

plotTHEMIS(data, t, site, fn)
