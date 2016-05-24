function A = randomAdjacency(n,k,l)

% Generate a random bipartite graph
% n students of degree k
% m assignments of degree l
% Need n * k = m * l, so just generate m
% Works well for k << n, l << m

% Initialize variables
T = n*k;
m = T / l;

A = zeros(n,m);

% Do a random permutation
% We may think of the m * l assignments as distinct
students = 1:T;
assignments = randperm(T);

% Take appropriate moduli to make the m * l assigmnets no longer distinct
students = ceil(students/k);
assignments = ceil(assignments/l);

% Update the adjacency matrix
for i = 1:T
    A(students(i),assignments(i)) = 1;
end

% If not all the edges were different, redraw to get a regular graph
if sum(sum(A)) < T
    A = randomAdjacency(n,k,l);
end

end

