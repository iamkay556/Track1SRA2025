% Makes a new auction
classdef AuctionClass
    properties
        % General
        id;             % Int/Array; Unique auction id

        % Unchanging
        commonVal;      % Int; Arbitrary common value
        rStndDv;        % Int; Standard deviation of signals from commonVal
        startPrice;     % Int; Initial price
        priceIncrement; % Int; Amount to increment price every step
        numBidders;     % Int; Total number of bidders
        bidderTypes;    % Matrix/Array; number of each bidder type
        bidders;        % Matrix/Array; all bidder objects

        % Unchanging Valuation Vars
        alpha1;          % Float; for BidderClass_strat1
        alpha2;          % Float; for BidderClass_strat2
        
        % Step-dependent 
        time;           % Int; Simulation current time
        price;          % Int; current price of object. Increases linearly.
        biddersIn;      % Matrix/Array; number of bidders still "in"
        dropOutTimes;   % Matrix/Array; times at which bidders drop out
        dropOutPrices;  % Matrix/Array; prices at which bidders drop out
        signals;        % Matrix/Array; signals of drop-outs

        % End Vars
        fprice;         % Int; selling price
        wintype;        % Int; winning bidder's type
    end


    methods
        % Assign ID
        function obj = setID(obj, id)
            obj.id = [id];
        end


        % Initialize variables of an auction
        function obj = setVars(obj, commonVal, rStndDv, startPrice, priceIncrement, alpha1, alpha2)
            % Initialize constant variables
            obj.commonVal = commonVal;
            obj.rStndDv = rStndDv;
            obj.startPrice = startPrice;
            obj.priceIncrement = priceIncrement;
            obj.numBidders = 0;         % Set in setBidders Function

            % Initialize constant valuation variables
            obj.alpha1 = alpha1;
            obj.alpha2 = alpha2;
            
            % Initialize step-dependent variables
            obj.time = 1;
            obj.biddersIn(1, 1) = 0;    % Set in setBidders Function
            obj.price = startPrice;     % Set starting price
        end
        

        % Sets up bidders matrix/array
        function obj = setBidders(obj, bidderTypes)
            obj.bidderTypes = bidderTypes;  % Records bidder type numbers
            
            % Set numBidders and biddersIn
            numTypes = length(obj.bidderTypes);
            for i = 1:numTypes
                obj.numBidders = obj.numBidders + obj.bidderTypes(1, i);
            end
            obj.biddersIn(1, 1) = obj.numBidders;
            
            % Create a cell array for bidder objects
            obj.bidders = cell(numTypes, max(obj.bidderTypes));

            % Create bidder objects
            % Loop through bidderTypes
            for i = 1:numTypes
                % Create corresponding bidder objects of type i
                for j = 1:obj.bidderTypes(1, i)
                    switch i
                        case 1
                            b = BidderClass_strat1();
                        case 2
                            b = BidderClass_strat2();
                    end

                    % Set-Up
                    b = b.setID(obj.id, i, j);
                    b = b.newBidder(normrnd(obj.commonVal, obj.rStndDv));

                    % v_zeros = [1200 951 936 903 992 1029 993 1081 1069 1245 836 683 946 1107 1100 809 984 793 1378 1012];
                    % b = b.newBidder(v_zeros(j + (i-1) * j));

                    obj.bidders{i, j} = b;
                end
            end

        end


        % Runs a simulation
        function obj = runSim(obj)
            % Display starting time and price
            %disp(["Time: ", num2str(obj.time)])
            %disp(["Price: ", num2str(obj.price)])

            while (obj.biddersIn > 0)
                obj = obj.timeStep();
            end
            
            disp("Simulation Finished.")
            
            % Find winner type and sets final price
            % In case there are multiple, the first is picked (essentially random)
            [m, n] = size(obj.bidders);
            found = false;
            for i = 1:m
                for j = 1:n
                    if (~isempty(obj.bidders{i, j}) & obj.bidders{i, j}.dropOutTime == obj.time)
                        obj.wintype = obj.bidders{i, j}.id(1, 2);

                        found = true;
                        break;
                    end
                end
                if (found)
                    break;
                end
            end

            if (obj.dropOutPrices(1, end) == obj.dropOutPrices(1, end-1))
                obj.fprice = obj.price - obj.priceIncrement;
            else
                obj.fprice = obj.dropOutPrices(1, end-1);
            end

            
            disp(["Winner Type: ", num2str(obj.wintype)])
            disp(["Selling Price: ", num2str(obj.fprice)])

        end


        % Increment time and run time-based actions
        function obj = timeStep(obj)
            obj.time = obj.time + 1;
            obj = obj.increasePrice();       % Increment the current price
            
            % disp(["Time: ", num2str(obj.time)])
            % disp(["Price: ", num2str(obj.price)])
            % disp(["Bidders In: ", num2str(obj.biddersIn(1, end))])
            
            % Drop-outs and valuation changes
            [m, n] = size(obj.bidders);
            obj.biddersIn(1, obj.time) = 0;
            for i = 1:m
                for j = 1:n
                    b = obj.bidders{i, j};

                    % Skips empty cells and past drop-outs
                    if (~isempty(b) & b.stillIn)
                        
                        % Update activity status
                        b = b.isDropping(obj.time, obj.price);
                        
                        % Update valuation if still in
                        if b.stillIn
                            switch b.id(1, 2)
                                case 1
                                    b = b.updateVal(obj.time, obj.numBidders, obj.biddersIn, obj.dropOutPrices, obj.price, obj.alpha1);
                                case 2
                                    b = b.updateVal(obj.time, obj.numBidders, obj.biddersIn, obj.dropOutPrices, obj.price, obj.alpha2);
                            end

                            % Update biddersIn tracker
                            obj.biddersIn(1, obj.time) = obj.biddersIn(1, obj.time) + 1;
                        else
                            obj.dropOutTimes(1, end + 1) = b.dropOutTime;
                            obj.dropOutPrices(1, end + 1) = b.dropOutPrice;
                            obj.signals(1, end  + 1) = b.signal;
                        end
                        
                    else
                        continue
                    end

                    % Add back to bidder
                    obj.bidders{i, j} = b;
                end
            end

        end
        

        % Increments current price
        function obj = increasePrice(obj)
            obj.price = obj.price + obj.priceIncrement;
        end


        % Displays Plots
        function obj = displayPlots(obj)
            t = 1:obj.time;

            figure;
            hold on;
            
            % Plot prices over time
            plot(t, obj.startPrice + (t * obj.priceIncrement));
            
            % Plot valuations over time
            [m, n] = size(obj.bidders);
            for i = 1:m
                for j = 1:n
                    if (~isempty(obj.bidders{i, j}))
                        y = obj.bidders{i, j}.vals;
                        plot(y)
                    end
                end
            end
        end

    end

end