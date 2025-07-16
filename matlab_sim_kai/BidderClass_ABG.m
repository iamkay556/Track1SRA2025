classdef BidderClass_ABG < BidderClass

    properties
        % alpha;    % Float; initial signal weighting in valuation function
    end

    methods
        % Update valuation
        function obj = updateVal(obj, time, numBidders, biddersInmtx, dropOutPrices, price)
            [~, l] = size(obj.vals);

            biddersOut = numBidders - biddersInmtx(time - 1);
            biddersIn = biddersInmtx(time - 1);

            a = obj.alpha;
            b = (1 - a) * (biddersOut / numBidders);
            g = (1 - a) * (biddersIn / numBidders);

            if (~isempty(dropOutPrices))
                avg = mean(dropOutPrices);
            else
                avg = 0;
            end

            P = price;

            obj.vals(1, l + 1) = a * obj.signal + b * avg + g * P;
        end
    end
end