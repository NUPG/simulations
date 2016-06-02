function [G,Gv] = initializeGuesses(D,P,n,m,A)

% D draws, P probability, both n by m matrices
% Generates n by m guess and variance matrices G, Gv

% Remove very large D values
X = D;
D(D >= 10^10) = 1;

% Draw from a binomial distribution
G = binornd(D,P,n,m);

% When D is 10^10, it knows the exact value
G(X >= 10^10) = P(X >= 10^10);

% Where D is 0, draw from uniform distribution on [0,1]
uniform = rand(n,m);
G(X==0) = uniform(X==0);

% Initialize variances to all be the same (1)
Gv = ones(n,m);

% Except nonexistent edges should have infinite variance
Gv(~A) = 10^10; 

end

