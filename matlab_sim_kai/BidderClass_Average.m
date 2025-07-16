classdef BidderClass_Average < BidderClass

    methods
        % Update valuation
        function obj = updateVal(obj, dropOutPrices)
            k = length(dropOutPrices);

            [~, l] = size(obj.vals);

            if (~isempty(dropOutPrices))
                avg = ((k * dropOutPrices(1, end)) + obj.signal) / (k + 1);
            else
                avg = obj.vals(1, l);
            end

            obj.vals(1, l + 1) = avg;
        end
    end
end