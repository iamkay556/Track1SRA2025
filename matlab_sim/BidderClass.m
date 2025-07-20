% Parent class for all bidders
classdef BidderClass
    properties
        % General properties
        id              % Int/Array; Unique bidder ID (auction ID, bidder type, type #)

        % Unchanging
        signal          % Int; Original valuation
        
        % Changing
        vals            % Matrix/Array; valuations over time
        stillIn         % Bool; true if in, false if dropped
        dropOutTime     % Int; empty if in, time step when dropped if out (>0)
        dropOutPrice    % Int; empty if in, price when dropped if out (>0)
    end

    methods
        % Assign ID
        function obj = setID(obj, auctionid, typeid, id)
            obj.id = [auctionid, typeid, id];
        end


        % Initialize variables of the bidder
        function obj = newBidder(obj, signal)
            % Initialize constant variables
            obj.signal = signal;
            
            % Initialize step-dependent variables
            obj.vals(1, 1) = signal;
            obj.stillIn = true;
            obj.dropOutTime = -1;
            obj.dropOutPrice = -1;
        end


        % See if currPrice >= val
        function obj = isDropping(obj, time, price)
            if price >= obj.vals(1, time - 1)
                obj.stillIn = false;            % Change dropped status
                obj.dropOutTime = time;         % Records current time step
                obj.dropOutPrice = price;       % Record current price

                obj.vals(1, time) = obj.vals(1, time - 1); % Adds one more point for the graph
            end
        end


        % Update valuation
        function obj = updateVal(obj)
            % [ change valuation here ]
        end

    end
    
end