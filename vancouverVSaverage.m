% Vancouver vs Simple Averaging

ppp = []; sss = [];

for m = 1:100
    run('vancouver.m');
end

figure;
plot(1:100,(ppp-0.4).^2);
title('Vancouver Error vs Number of Assignments');

figure;
plot(1:100,(sss-0.4).^2);
title('Simple Averaging Error vs Number of Assignments');