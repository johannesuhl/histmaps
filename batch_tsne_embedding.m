%% code from http://cs.stanford.edu/people/karpathy/cnnembed/cnnembed.zip
%% credits: Andrej Karpathy, Stanford Computer Science
%% modified by Johannes Uhl, University of Colorado, Department of Geography

function y = create_tSNE_map(outname,coord_file,filenames,thumbnail_size)

disp(coord_file)
disp(filenames)

%% load embedding

coords = load(coord_file); % load x (the embedding 2d locations from tsne)

x = bsxfun(@minus, coords, min(coords));
x = bsxfun(@rdivide, x, max(x));

%% load validation image filenames

fs = textread(filenames, '%s');
N = length(fs);

%% create an embedding image

S = 4000; % size of full embedding image
G = zeros(S, S, 3, 'uint8');
s = thumbnail_size; % size of every single image, was 50, 30

Ntake = N;
for i=1:Ntake
    
    if mod(i, 100)==0
        fprintf('%d/%d...\n', i, Ntake);
    end
    
    % location
    a = ceil(x(i, 1) * (S-s)+1);
    b = ceil(x(i, 2) * (S-s)+1);
    a = a-mod(a-1,s)+1;
    b = b-mod(b-1,s)+1;
    if G(a,b,1) ~= 0
        continue % spot already filled
    end
    
    I = imread(fs{i});
    if size(I,3)==1, I = cat(3,I,I,I); end
    I = imresize(I, [s, s]);
    
    G(a:a+s-1, b:b+s-1, :) = I;
    
end
%% imshow(G);
outfile = strcat('t-SNE_map_1_',outname,'.jpg')
imwrite(G, outfile);


%% do a guaranteed quade grid layout by taking nearest neighbor

S = 2000; % size of final image
G = zeros(S, S, 3, 'uint8');
s = thumbnail_size; % size of every image thumbnail

xnum = S/s;
ynum = S/s;
used = false(N, 1);

qq=length(1:s:S);
abes = zeros(qq*2,2);
i=1;
for a=1:s:S
    for b=1:s:S
        abes(i,:) = [a,b];
        i=i+1;
    end
end
%abes = abes(randperm(size(abes,1)),:); % randperm

for i=1:size(abes,1)

    a = abes(i,1);
    b = abes(i,2);
    %xf = ((a-1)/S - 0.5)/2 + 0.5; % zooming into middle a bit
    %yf = ((b-1)/S - 0.5)/2 + 0.5;
    xf = (a-1)/S;
    yf = (b-1)/S;
    dd = sum(bsxfun(@minus, x, [xf, yf]).^2,2);
    dd(used) = inf; % dont pick these
    [dv,di] = min(dd); % find nearest image

    used(di) = true; % mark as done
    I = imread(fs{di});
    if size(I,3)==1, I = cat(3,I,I,I); end
    I = imresize(I, [s, s]);

    G(a:a+s-1, b:b+s-1, :) = I;

    if mod(i,100)==0
        fprintf('%d/%d\n', i, size(abes,1));
    end
end

%% imshow(G);
outfile = strcat('t-SNE_map_2_',outname,'.jpg')
imwrite(G, outfile, 'jpg');

quit
end
