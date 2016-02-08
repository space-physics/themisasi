function var2hdf,v,n,fid
; takes care of repetitive verbose hdf5 file writing for each plain array variable.
dt = h5t_idl_create(v)
ds = h5s_create_simple(size(v,/dimensions))
d=h5d_create(fid,n,dt,ds,gzip=4,/shuffle)
h5d_write,d,v
return,fid
end

function var2nc,v,n,fid,x,y
;  writer for NetCDF
print,n
h = ncdf_vardef(fid,n,[x,y],/double) ; no gzip for gdl
ncdf_control,fid,/endef
ncdf_varput,fid,h,v
ncdf_control,fid,/redef
return,fid
end

PRO SAV2HDF5, fin
; This example created for rescuing corrupted THEMIS GBO ASI .sav files 
; that were unreadable by other means such as scipy.io.readsav
; Michael Hirsch Jan 2016

COMPILE_OPT idl2

stem = strsplit(fin,'.',/extract)
fout=(strjoin(stem[0],'.nc'))


; read input
cmrestore,fin
print,'read skymap'
;help,skymap



el = skymap.full_elevation
az = skymap.full_azimuth
lla = [skymap.SITE_MAP_LATITUDE,skymap.site_map_longitude,skymap.site_map_altitude]

;
; write to HDF5
;
print,'writing to'
print,fout

; method below writes HDF5 in a lousy compound format
;dat = {az:az, el:el,lat:lat,lon:lon}
;ds = {_NAME:'azel',_TYPE:'dataset',_DATA:dat}
;h5_create,fout,ds

; works in IDL, not in GDL
;fid = h5f_create(fout)
;fid = var2hdf(az,'az',fid)
;fid = var2hdf(el,'el',fid)
;fid = var2hdf(lla,'lla',fid)
;h5f_close,fid

; works in GDL & IDL

rc = size(az,/dimensions)
fid = ncdf_create(fout,/clobber)

x = ncdf_dimdef(fid,'x',rc[1]) 
y = ncdf_dimdef(fid,'y',rc[0]) 

fid = var2nc(az,'az',fid,x,y)
fid = var2nc(el,'el',fid,x,y)

len = ncdf_dimdef(fid,'len',3) ; meh
one = ncdf_dimdef(fid,'one',1)
fid=var2nc(lla,'lla',fid,len,one)

ncdf_close,fid

END
