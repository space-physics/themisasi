% reference: http://themis.ssl.berkeley.edu/gbo/THEMIS_All_Sky_Imager-2.pdf
% high-res (256x256 pixel) data: http://themis.ssl.berkeley.edu/data/themis/thg/l1/asi
% low-res (64x64 thumbnail pixel) data: http://themis.ssl.berkeley.edu/data/themis/thg/l0/asi/
%
% info
% http://themis.ssl.berkeley.edu/instrument_asi.shtml
%
% sites that saw HiST:
% fykn: http://themis.ssl.berkeley.edu/data/themis/thg/l1/asi/fykn/2013/04

function [data,t,hdrs, site] = readTHEMIS(file, fullthumb)
arguments
  file (1,1) string {mustBeFile}
  fullthumb (1,1) string = "f" %f for full, t for thumb
end

[~,filename] = fileparts(file);

site = regexp(filename,'(?<=thg_l\d_as\w_)\w{4}', match='once');
disp("site: " + site)

%% read data
hdrs = cdfinfo(file);

%format of variableNames is by column:
% 1) variable name
% 2) size (dimensions) of variable
% 3) # of records for the variable
% 4) data type of variable (CDF)
% 5) see doc cdfinfo

v = "thg_as" + fullthumb + "_" + site + "_epoch";
disp(file + " < " + v)
t = cdfread(file, Variables=v, DatetimeType="datetime", CombineRecords=true);

% v = v + "0";
% disp(file + " < " + v)
% epoch0 = cdfread(file, Variables=v, CombineRecords=true);

% this isn't matlab datenum, since 0AD?
% CDFt = cdfread(file, Variables=['thg_as',ft,'_',site,'_time'], CombineRecords=true);

v = "thg_as" + fullthumb + "_" + site;
disp(file + " < " + v)
data = cdfread(file, Variables=v, DatetimeType="datetime", Combinerecords=true);
end
