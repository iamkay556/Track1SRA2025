classdef CustomAlphaBidder < handle
    % Custom bidder class that accepts any alpha value for ABG valuation
    
    properties
        id
        signal
        vals
        stillIn
        dropOutTime
        dropOutPrice
        alpha
    end
    
    methods
        function obj = CustomAlphaBidder(alphaValue)
            obj.alpha = alphaValue;
        end
        
        function obj = setID(obj, auctionID, typeID, bidderID)
            obj.id = [auctionID, typeID, bidderID];
        end
        
        function obj = newBidder(obj, signal)
            obj.signal = signal;
            obj.vals = signal;
            obj.stillIn = true;
            obj.dropOutTime = -1;
            obj.dropOutPrice = -1;
        end
        
        function obj = updateVal(obj, time, numBidders, currentPrice, dropOutPrices)
            if ~obj.stillIn
                return;
            end
            
            % Calculate bidders in/out
            biddersOut = length(dropOutPrices);
            biddersIn = numBidders - biddersOut;
            
            % ABG valuation function: V = αS + β*avgDropout + γ*currentPrice
            % where β + γ = (1-α) and β/γ = biddersOut/biddersIn
            a = obj.alpha;
            b = (1 - a) * (biddersOut / numBidders);
            g = (1 - a) * (biddersIn / numBidders);
            
            if ~isempty(dropOutPrices)
                avgDropoutPrice = mean(dropOutPrices);
            else
                avgDropoutPrice = 0;
            end
            
            newVal = a * obj.signal + b * avgDropoutPrice + g * currentPrice;
            obj.vals(end+1) = newVal;
        end
    end
end