classdef BidderClass_Rational < BidderClass

    methods
        % Update valuation
        function obj = updateVal(obj, time, numBidders, biddersInmtx, dropOutPrices, price, alpha)
            
            [~, l] = size(obj.vals);

            biddersOut = numBidders - biddersInmtx(time - 1);
            biddersIn = biddersInmtx(time - 1);

            a = obj.alpha;
            b = (1 - alpha) * (biddersOut/numBidders);
            c = (1 - alpha) * (biddersIn/numBidders);

            if (~isempty(dropOutPrices))
                avg = mean(dropOutPrices); 
            else
                avg = 0;
            end
            
            P = price;
        
            % obj.vals(1, l + 1) = a * obj.vals(1, l) + b * avg + c * P;
            obj.vals(1, l+1) = a * obj.signal + b * avg + c * P;
        end
    end
end