function [M,G,p,average,weighted] = runVancouver(n,m,l,k,d,p,N,A)

%% Notes about this model
% True assignment grade is p
% Student draws d times from bernoulli distribution with probability p
% Student obtains sample mean s from this sample
% Student then draws their reported score from Beta(s,d-s)

%% Inputs
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
% p may also be a singleton

% N is the number of iterations

% A is an adjacency matrix, n by m.
% This is generated unless the user specifies some A
% A(i,j) = 1 if and only if student i will grade assignment j

%% Modes
% If n, l, k are provided, m can be calculated
% In this mode, if A is not provided, it can be randomly generated

% If n, m are provided, but l, k are not, then the graph is assumed to be a
% complete bipartite graph.

%% Outputs
% Algorithm guessed grades, a 1 by m vector M
% Student guessed grades, an n by m matrix G
% Actual grades, a 1 by m vector p
% Simple average, a 1 by m vector average
% Weighted average, a 1 by m vector weighted

%% Fix up the inputs

% Generate m, p as needed
if (m < 0)
    m = n * k / l;
end

if (p < 0)
    p = rand(1,m);
end

% Generate n by m adjacency, with A(i,j) = 1 iff i grades j
if (nargin == 7) || (A < 0)
    if (l <= 0)
        A = ones(n,m);
    else
        A = randomAdjacency(n,k,l);
    end
end

% For convenience, the vectors are turned into n by m matrices
% P(i,j) is the true grade of j
% D(i,j) is the number of draws of student i
if length(p) == 1
    P = repmat(p,n,m);
else
    P = repmat(p,n,1);
end
if length(d) == 1
    D = repmat(d,n,m);
else
    D = repmat(d',1,m);
end

%% Running the algorithm

[G,Gv] = initializeGuesses(D,P,n,m,A); % Draw the guesses

for i = 1:N
        
        % Get the variance weighted estimate of the grades, row vector M
        % s is the variance on each of the guesses in M
        
        [M,s] = varianceWeightedEstimate(G,Gv,1);

        % We cannot have s = 0, so set s to be arbitrarily small
        s(s < 10^-10) = 10^-10;

        % Make into matrices for convenience
        % M(i,j) is the algorithm guessed grade of assignment j
        M = repmat(M,n,1);
        s = repmat(s,n,1);

        % Student guessed grades minus algorithm guessed grades, squared
        errors = (G - M).^2;

        % New variance on the grades is the errors weighted by s (errors on
        % the assignment grades themselves)
        [newGv,~] = varianceWeightedEstimate(errors,s,2);

        % Again, cannot have 0 variance
        newGv(newGv < 10^-10) = 10^-10;

        % Set new Gv
        Gv = repmat(newGv,1,m);
        
        % Ensure that we set the nonexistent edges to have infinite
        % variance
        Gv(~A) = 10^10;

end

% Get the row vector of the algorithm estimates of the grade
[M,~] = varianceWeightedEstimate(G,Gv,1);

% Simple average
average = sum(G)/n;

% Weighted average
weighted = sum(G.*D)./sum(D);

end