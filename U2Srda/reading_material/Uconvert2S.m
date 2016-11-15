clc; clear all;close all;
dcmfile      = dir('./*.dcm');
dcmfilename  = dcmfile.name;
UIHData      = dicominfo(dcmfilename);
UIHSpectro   = UIHData.SpectroscopyData;
UIHNewSpectro  =  double(UIHSpectro);

rdafile      = dir('./*.txt');
rdafilename  = rdafile.name;
if(~exist(rdafilename))
    disp(['no rda demo. please input one.'])
end

%%%%%1.Read Siemens RDA Data and copy%%%%%%%%%
SiemensRdaFid  = fopen(rdafilename, 'r+');
head_start_text = '>>> Begin of header <<<';
head_end_text   = '>>> End of header <<<';

Stline = fgets(SiemensRdaFid);
LineCount = 0;
while(isempty(strfind(Stline , head_end_text)))
    Stline = fgets(SiemensRdaFid);
    occurence_of_colon = findstr(':',Stline);
    value    = Stline(occurence_of_colon+1 : length(Stline)) ;
    disp(['value:' num2str(value)]);
    
    LineCount = LineCount+1;
end
if(~isempty(strfind(Stline , head_end_text)))
    disp(['linenumber' num2str(LineCount)]);
end

fwrite(SiemensRdaFid, UIHNewSpectro,'double');

