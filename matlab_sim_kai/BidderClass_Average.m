classdef BidderClass_Average < BidderClass

    methods
        % Update valuation
        function obj = updateVal(obj, signals)

            [~, l] = size(obj.vals);

            if (~isempty(signals))
                avg = (sum(signals) + obj.signal) / (length(signals) + 1);
            else
                avg = obj.vals(1, l);
            end

            obj.vals(1, l + 1) = avg;
        end
    end
end