function [data,t,hdrs] = getTHEMIS(varargin)
% Michael Hirsch, Dec 2013
% Boston University
% reference: http://themis.ssl.berkeley.edu/gbo/THEMIS_All_Sky_Imager-2.pdf
% high-res (256x256 pixel) data: http://themis.ssl.berkeley.edu/data/themis/thg/l1/asi
% low-res (64x64 thumbnail pixel) data: http://themis.ssl.berkeley.edu/data/themis/thg/l0/asi/
%
% info
% http://themis.ssl.berkeley.edu/instrument_asi.shtml
%
% sites that saw HST:
% fykn: http://themis.ssl.berkeley.edu/data/themis/thg/l1/asi/fykn/2013/04
%%

p = inputParser();
addRequired(p,'fn')
addOptional(p,'path','~/data')
addParamValue(p,'startind',1) %#ok<*NVREPL>
addParamValue(p,'stopind',[])
addParamValue(p,'writevid',false)
addParamValue(p,'writefits',false)
addParamValue(p,'fullthumb','f')%f for full, t for thumb
p.parse(varargin{:})
U = p.Results;

site = regexp(U.fn,'(?<=thg_l\d_as\w_)\w{4}(?=_.*.cdf)','match','once');
display([' site: ',site])

%% select clims for imagesc() (arbitrary for best viewing contrast)
switch site
    case {'gako','fykn'}, clims=[2200 10e3];
    case {'mcgr'}, clims=[2200 5000];
    otherwise, clims = [0 3000];
end
%% read data


dfn = [U.path,filesep,U.fn];

hdrs = cdfinfo(dfn);

%format of variableNames is by column:
% 1) variable name
% 2) size (dimensions) of variable
% 3) # of records for the variable
% 4) data type of variable (CDF)
% 5) see doc cdfinfo
variableNames = hdrs.Variables;

t = cdfread(dfn,'variable',['thg_as',U.fullthumb,'_',site,'_epoch'],...
          'convertepochtodatenum',true,'combineRecords',true);
epoch0 = cdfread(dfn,'variable',['thg_as',ft,'_',site,'_epoch0'],...
          'convertepochtodatenum',true,'combineRecords',true);

% this isn't matlab datenum--how to convert?
% CDFt = cdfread(dfn,'variable',['thg_as',ft,'_',site,'_time'],...
%              'convertepochtodatenum',true,'combineRecords',true);

data = cdfread(dfn,'variable',['thg_as',ft,'_',site],'combinerecords',true);

Nrec = length(t);
if isempty(U.stopind), U.stopind = Nrec; end
%% plotting
currFrame = squeeze(data(1,:,:));

hf = figure(1); clf(1)
ax = axes('parent',hf);
hi = imagesc(currFrame,clims);
set(ax,'ydir','normal')
ht= title('','interpreter','none');
xlabel('x-pixel')
ylabel('y-pixel')
colorbar
colormap gray

figure(2),clf(2)
imhist(currFrame)
title(['First frame histogram: ',datestr(t(1))])

display(['Showing frames from ',int2str(startInd),' to ',int2str(stopInd)])

[~,dstem] = fileparts(U.fn); %for PNG | AVI
if U.writevid
    vidFN = [U.path,filesep,dstem,'.avi'];
    vwObj = VideoWriter(vidFN,'Motion JPEG AVI');
    vwObj.FrameRate = 4; %VLC can't playback less than 4fps--very old VLC bug
    vwObj.Quality = 90;
    open(vwObj)
    display(['Writing MJPEG AVI ',vidFN])
else
    vwObj = [];
end

for i = startInd:stopInd
    currFrame = squeeze(data(i,:,:));
    colorbar
    set(ht,'string',{U.fn,...
                   [datestr(t(i)),'UT,  iCDF= ',int2str(i),'/',int2str(Nrec)]})
    set(hi,'cdata',currFrame)

    if U.writevid
       gf = getframe(hf);
       writeVideo(vwObj,gf);
    end

    if U.writefits
       FITSfn = [path,filesep,dstem,'_',int2str(i),'.fits'];
       display(['writing to ',FITSfn])
       fitswrite(int32(currFrame),FITSfn) %haven't tried compression yet
    end

pause(0.01)
end %for

close(vwObj);

if nargout==0, clear, end

end %fcn
