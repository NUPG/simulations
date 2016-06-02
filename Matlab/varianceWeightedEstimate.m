function [m,s] = varianceWeightedEstimate(X,V,i)

% Gives the variance weighted estimate
% X, V are the same size (V is the variance of guesses in X)
% Find the variance-weighted average of each column/row, return row/column vector
% Mode 1, 2 picks to average columns, rows respectively

m = sum(X./V,i)./sum(1./V,i);
s = sum(1./V,i).^(-1);

end

