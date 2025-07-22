% Custom bidder class with configurable alpha value
classdef CustomBidder < BidderClass_ABG
    properties
        alpha % Float; configurable alpha value
    end
    
    methods
        function obj = CustomBidder(alphaValue)
            % Constructor that sets the alpha value
            if nargin > 0
                obj.alpha = alphaValue;
            else
                obj.alpha = 0.5; % default value
            end
        end
    end
end