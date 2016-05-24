global count;

averageCount = 0;
N = 10000;

for i = 1:N
    randomAdjacency(100,3,5,1);
    averageCount = averageCount + count/N;
end

disp(1/averageCount);