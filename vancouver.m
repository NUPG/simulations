% Various settings allowed
% Select the number of iterations -- add "until convergence" case?

% Select one or many choices for the number of students
    % can also repeat elements in the array for multiple trials
    % use repitions for this

% Select quality d, if fixed, or vector d, if you want it to vary for each
    % n; if you select an nRange, you have  to put d(n) in the loop

% Select m, the number of assignments
% set p, random vector of length m, or constant vector of length m
% Select if you want to do beta or not


% Iterations
N = 100; 

k = 3; l = 5;

% Students
% Set d here; vector of length n
%nRange = [1 2 4 5 10 20 25 50 100];
nRange = l:l:500;
repetitions = 100;
%d = [1000000*ones(1,10),zeros(1,40)];
%d = 1:90;
%d = [ones(1,60)*1000,ones(1,30)*1];
%d = [1,1,1,1,1,1];

% Assignments
% Set p here; vector of length m
%m = 10;

%p = 0.4*ones(1,m);
%p = rand(1,m);

% guess = zeros(length(nRange),m);
% guessError = guess;
% simpleAverage = guess;
% simpleAverageError = guess;
% weightedAverage = guess;
% weightedAverageError = guess;
% repGuesses = zeros(m,repetitions);
% repSimple = zeros(m,repetitions);

% varCheck = 0;
% if m*length(nRange) == 1
%     varCheck = 1;
%     guessVariance = zeros(1,N+1);
% end

for j = 1:length(nRange)
    for iter = 1:repetitions
        n = nRange(j);
        d = [10^9 * ones(1,n/5), zeros(1,4*n/5)];
        m = n * k / l;
        p = 0.4 * ones(1,m);
        %d = round(200/n);
        %d = [ones(1,round(99/6)-n/6)*6,ones(1,n)];
        %n = length(d);
        %d = [1000*ones(1,n),2*ones(1,100-n)];
        %n = 100;
        % Setting up some variables
        P = repmat(p,n,1);
        if length(d) == 1
            D = repmat(d,n,m);
        else
            D = repmat(d',1,m);
        end

        % Generate student scores; Gij = student i's score of assignment j
        A = randomAdjacency(n,k,l);
        [G,Gv] = initializeGuesses(D,P,n,m,A);
       
        %if varCheck
        %    guessVariance(1) = 1;
        %end

        %simpleAverage(j,:) = simpleAverage(j,:) + sum(G,1)/(n*repetitions);
        %simpleAverageError(j,:) = simpleAverageError(j,:) + (sum(G,1)/n-p).^2/repetitions;
        %repSimple(:,iter) = sum(G,1)/n;
        %weightedAverage(j,:) = weightedAverage(j,:) + sum(G' .* d,1) / (sum(d,1) * repetitions);
        %weightedAverageError(j,:) = weightedAverageError(j,:) + (sum(G' .* d,1) / sum(d,1) - p).^2/repetitions;
        
        % Run vancouver
        for i = 1:N

            [M,s] = varianceWeightedEstimate(G,Gv,1);

            s(s < 0.0000001) = .0000001;

%             if varCheck
%                 guessVariance(i+1) = s;
%             end
            
            M = repmat(M,n,1);
            s = repmat(s,n,1);

            errors = (G - M).^2;

            [newGv,~] = varianceWeightedEstimate(errors,s,2);

            newGv(newGv < 10^-7) = 10^-7;

            Gv = repmat(newGv,1,m);

        end

        [M,s] = varianceWeightedEstimate(G,Gv,1);
        repGuesses(:,iter) = M;
        guess(j,:) = guess(j,:) + M/repetitions;
        guessError(j,:) = guessError(j,:) + (M-p).^2/repetitions;
        
    end
end

if length(nRange) == 1
    fprintf('p-value: %f\n',mean(p));
    fprintf('estimate: %f\n',mean(guess));
    ppp = [ppp, mean(guess)];
    fprintf('simple average: %f\n',mean(simpleAverage));
    sss = [sss, mean(simpleAverage)];
    if varCheck
        %fprintf('guess variance: %f\n',guessVariance(N+1));
    end
end

if (m == 1) && ~(varCheck)
    %figure;
    %plot(nRange,smooth(smooth(smooth(guess))));
    %title('Guess (smooth) vs Number of Students');
    %hold on;
    %plot(nRange,ones(size(nRange))*p,'r');
    %hold off;
    figure;
    plot(nRange,guess);
    title('Guess vs Number of Bad Students');
    hold on;
    plot(nRange,ones(size(nRange))*p,'r');
    plot(nRange,simpleAverage,'g');
    plot(nRange,weightedAverage,'y');
    hold off;
    figure;
    plot(nRange,guessError);
    hold on;
    plot(nRange,simpleAverageError,'g');
    plot(nRange,weightedAverageError,'y');
    hold off;
    title('Error vs Number of Bad Students');
end

% edges = 0.1:0.1:0.8;
% figure; histogram(repGuesses,10); 
% figure; histogram(repSimple,10);
% figure; histogram((repGuesses * 3 - .4)/2,10);

if varCheck
    %plot(0:N,guessVariance);
    %title('Guess variance vs Iteration');
end