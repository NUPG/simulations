% Main file to run Vancouver algorithm

%% Uses call to "runVancouver.m"
% Notes about this model
% True assignment grade is p
% Student draws d times from bernoulli distribution with probability p
% Student obtains sample mean s from this sample
% Student then draws their reported score from Beta(s,d-s)

% Inputs
% n is the number of students
% m is the number of assignments
% l is the degree of an assignment
% k is the degree of a student

% d is a row vector of length n indicating the number of draws for each
% student
% Alternatively, d can be a single value, which will indicate each student
% gets the same number of draws
% d = 0 indicates drawing from a uniform distribution
% d -> +inf indicates the student knows the exact score

% p is a row vector of length m of grades of assignments (0 <= p(i) <= 1)
% If p is not provided (i.e. if p < 0) it is randomly generated.

% N is the number of iterations

% A is an adjacency matrix, n by m.
% This is generated unless the user specifies some A
% A(i,j) = 1 if and only if student i will grade assignment j

% Modes
% If n, l, k are provided, m can be calculated
% In this mode, if A is not provided, it can be randomly generated

% If n, m are provided, but l, k are not, then the graph is assumed to be a
% complete bipartite graph.

% Outputs
% Algorithm guessed grades, a 1 by m vector M
% Student guessed grades, an n by m matrix G
% Actual grades, a 1 by m vector p

%% Main
% Iterations
N = 1000;

% Trials
trials = 1;

% Some parameters
% k, degree of students
k = -1;
% l, degree of assignments
l = -1;

% range of choices of n
%nRange = l:l:100;
nRange = 3;

% range of choices of m
mRange = 1:100;

% errors(m)
errors = zeros(length(nRange),length(mRange),trials);
averageErrors = errors;
weightedErrors = errors;

for nIndex = 1:length(nRange)
    for mIndex = 1:length(mRange)
        for j = 1:trials
            
            n = nRange(nIndex);
            m = mRange(mIndex);
            
            % d (1 by n or 1 by 1)
            d = [0, 0, 10^10];

            % p (1 by m)
            p = 0.4;

            % A (need not specify)
            A = -1;

            [M,G,p,average,weighted] = runVancouver(n,m,l,k,d,p,N,A);
            errors(nIndex,mIndex,j) = (M(1) - p(1)).^2;
            averageErrors(nIndex,mIndex,j) = (average(1)-p(1)).^2;
            weightedErrors(nIndex,mIndex,j) = (weighted(1) - p(1)).^2;
        end
    end
end


% Errors vs # of Assignments ( n = 3, m Range = 1:100, p = 0.4)
plot(mRange,errors(:,:,1)); figure; plot(mRange,averageErrors(:,:,1)); figure; plot(mRange,weightedErrors(:,:,1));

% Errors of random assignments (k = 3, l = 5)
% plot(nRange,errors(:,1,1)); title('k = 3, l = 5, Error vs Number of Students');