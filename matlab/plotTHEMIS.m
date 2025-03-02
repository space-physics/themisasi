function plotTHEMIS(data, t, site, file, writeVid)
arguments
  data
  t datetime
  site (1,1) string
  file (1,1) string
  writeVid (1,1) logical = true
end


%% select clims for imagesc() (arbitrary for best viewing contrast)
switch site
  case {'gako','fykn'}, clims=[2200 10e3];
  case {'mcgr'}, clims=[2200 5000];
  otherwise, clims = [0 3000];
end

currFrame = squeeze(data(1,:,:));

hf = figure(1);
clf(hf)
ax = axes(parent=hf);
hi = imagesc(currFrame,clims);
set(ax, ydir='normal')
ht= title('', interpreter='none');
xlabel('x-pixel')
ylabel('y-pixel')
colorbar(ax)
colormap(ax, "gray")

addons = matlab.addons.installedAddons();
if contains(addons.Name, "Image Processing Toolbox")
  f2 = figure(2);
  ax = axes(parent=f2);
  imhist(ax, currFrame)
  title(ax, "First frame histogram: " + string(t(1)))
end


if writeVid
  [dir, filename] = fileparts(file);
  vidFN = fullfile(dir, filename + ".avi");
  vwObj = VideoWriter(vidFN, 'Motion JPEG AVI');
  vwObj.FrameRate = 4; %VLC can't playback less than 4fps--very old VLC bug
  vwObj.Quality = 90;
  open(vwObj)
  disp("Writing MJPEG AVI " + vidFN)
else
  vwObj = [];
end

for i = 1:length(t)
  currFrame = squeeze(data(i,:,:));
  set(ht, string={filename, string(t(i)) + "UT,  iCDF= " + int2str(i) + "/" + int2str(length(t))})
  set(hi, cdata=currFrame)

  if writeVid
    gf = getframe(hf);
    writeVideo(vwObj,gf);
  end

  pause(0.1)
end

close(vwObj);

end
