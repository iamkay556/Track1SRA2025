% Bidder with averaging bidder strategy
classdef BidderClass_Average < BidderClass

    methods
        % Update valuation
        function obj = updateVal(obj, dropOutPrices)
            k = length(dropOutPrices);

            [~, l] = size(obj.vals);
            
            % Default is same valuation
            avg = obj.vals(1, l);
            if (k > 0)
                avg = ((k * dropOutPrices(1, end)) + obj.signal) / (k + 1);
            end            
            
            % Update
            obj.vals(1, l + 1) = avg;

        end
    end
end