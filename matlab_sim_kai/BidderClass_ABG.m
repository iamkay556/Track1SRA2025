classdef BidderClass_ABG < BidderClass

    methods
        % Update valuation
        function obj = updateVal(obj, time, numBidders, biddersInmtx, dropOutPrices, price, alpha)
            [~, l] = size(obj.vals);

            biddersOut = numBidders - biddersInmtx(time - 1);
            biddersIn = biddersInmtx(time - 1);

            a = alpha;
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