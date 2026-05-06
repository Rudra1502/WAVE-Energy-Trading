'use strict';

const { Contract } = require('fabric-contract-api');

function getValidatorKey(id) {
    return `VALIDATOR_${id}`;
}

class V2VContract extends Contract {

    async initLedger(ctx) {
        console.log("Ledger initialized");
    }


    async registerEV(ctx, evId) {

        const exists = await ctx.stub.getState(evId);
        if (exists && exists.length > 0) {
            throw new Error("EV already registered");
        }

        const ev = {
            id: evId,
            reputation: 0,
            totalTrades: 0,
            successfulTrades: 0,
            avgLatency: 0,
            lastLatency: 0
        };

        await ctx.stub.putState(evId, Buffer.from(JSON.stringify(ev)));

        return JSON.stringify(ev);
    }

    async registerValidator(ctx, validatorId, energy) {

        const key = getValidatorKey(validatorId);
        const exists = await ctx.stub.getState(key);

        if (exists && exists.length > 0) {
            throw new Error("Validator already exists");
        }

        const validator = {
            id: validatorId,

            // 🔹 core metrics
            reputation: 0,
            totalValidations: 0,
            successfulValidations: 0,

            // 🔹 performance tracking
            successRate: 0,
            avgLatency: 0,
            lastLatency: 0,

            // 🔹 optional (for future extensions)
            energy: parseFloat(energy)
        };

        await ctx.stub.putState(key, Buffer.from(JSON.stringify(validator)));

        return JSON.stringify(validator);
    }

    async updateValidatorMetrics(ctx, validatorId, latency, isCorrect) {

        const key = getValidatorKey(validatorId);
        const data = await ctx.stub.getState(key);

        if (!data || data.length === 0) {
            throw new Error("Validator not found");
        }

        const validator = JSON.parse(data.toString());

        const latencyVal = parseFloat(latency);

        // ✅ normalize latency
        const latencyScore = 1 / (1 + latencyVal);

        // ✅ robust boolean handling
        const isValid = (isCorrect === true || isCorrect === "true");

        const correctnessScore = isValid ? 1 : -1;

        // ==============================
        // UPDATE STATS FIRST
        // ==============================
        validator.totalValidations += 1;

        if (isValid) {
            validator.successfulValidations += 1;
        }

        // ✅ success rate update
        validator.successRate =
            validator.successfulValidations / validator.totalValidations;

        // ==============================
        // LATENCY TRACKING
        // ==============================

        // moving average latency
        validator.avgLatency =
            (validator.avgLatency * (validator.totalValidations - 1) + latencyVal)
            / validator.totalValidations;

        validator.lastLatency = latencyVal;

        // ==============================
        // PARTICIPATION SCORE
        // ==============================
        const participationScore = validator.successRate;

        // ==============================
        // WEIGHTS
        // ==============================
        const alpha = 0.5;  // correctness
        const beta = 0.3;   // latency
        const gamma = 0.2;  // participation

        const reward =
            alpha * correctnessScore +
            beta * latencyScore +
            gamma * participationScore;

        // ==============================
        // DYNAMIC REPUTATION UPDATE
        // ==============================

        validator.reputation =
            0.7 * validator.reputation + 0.3 * reward;

        // Optional: clamp reputation (recommended)
        if (validator.reputation > 1) validator.reputation = 1;
        if (validator.reputation < -1) validator.reputation = -1;

        await ctx.stub.putState(key, Buffer.from(JSON.stringify(validator)));

        return JSON.stringify({
            validatorId,
            reward,
            updatedReputation: validator.reputation,
            successRate: validator.successRate,
            avgLatency: validator.avgLatency
        });
    }

    async selectValidator(ctx, mode) {
        // Mode is now a runtime parameter ("baseline" or "proposed")
        if (!mode) mode = "proposed";

        const iterator = await ctx.stub.getStateByRange('', '');
        let validators = [];

        let res = await iterator.next();
        while (!res.done) {
            const key = res.value.key;

            if (key.startsWith("VALIDATOR_")) {
                const val = JSON.parse(res.value.value.toString());

                const reputation = val.reputation || 0;
                const successRate = val.successRate || 0;
                const avgLatency = val.avgLatency || 1;

                const latencyScore = 1 / (1 + avgLatency);

                const alpha = 0.5;
                const beta = 0.3;
                const gamma = 0.2;

                const score =
                    alpha * reputation +
                    beta * successRate +
                    gamma * latencyScore;

                val.score = score > 0 ? score : 0.05; // avoid zero
                validators.push(val);
            }

            res = await iterator.next();
        }


        if (validators.length === 0) {
            throw new Error("No validators available");
        }

        // ==============================
        // SELECTION MODE SWITCH
        // ==============================

        if (mode === "baseline") {
            // 🔴 Deterministic (PoR-like)
            validators.sort((a, b) => b.reputation - a.reputation);
            return JSON.stringify(validators[0]);
        }

        // 🟢 Weighted probabilistic selection (proposed)
        const totalScore = validators.reduce((sum, v) => sum + v.score, 0);

        let rand = Math.random() * totalScore;

        for (let v of validators) {
            rand -= v.score;
            if (rand <= 0) {
                return JSON.stringify(v);
            }
        }

        return JSON.stringify(validators[validators.length - 1]);
    }


    // async submitPlan(ctx, evId, type, energy, price) {
        
    //     if (isNaN(energy) || isNaN(price)) {
    //         throw new Error("Invalid numeric values");
    //     }

    //     if (type !== "buyer" && type !== "seller") {
    //         throw new Error("Type must be either 'buyer' or 'seller'");
    //     }

    //     const evBytes = await ctx.stub.getState(evId);
    //     if (!evBytes || evBytes.length === 0) {
    //         throw new Error("EV not registered");
    //     }

    //     const txId = ctx.stub.getTxID();

    //     const plan = {
    //         txId: txId,
    //         evId: evId,
    //         type: type.toLowerCase(),   
    //         energy: parseFloat(energy),
    //         price: parseFloat(price),
    //         timestamp: new Date().toISOString()
    //     };

    //     await ctx.stub.putState(txId, Buffer.from(JSON.stringify(plan)));
    //     return JSON.stringify(plan);
    // }

    // async matchTransaction(ctx, buyerId, sellerId, energy) {

    //     const buyerBytes = await ctx.stub.getState(buyerId);
    //     const sellerBytes = await ctx.stub.getState(sellerId);

    //     if (!buyerBytes || !sellerBytes) {
    //         throw new Error("Invalid pseudonymous IDs");
    //     }

    //     const txId = ctx.stub.getTxID();

    //     const match = {
    //         txId,
    //         buyer: buyerId,
    //         seller: sellerId,
    //         energy: parseFloat(energy),
    //         status: "matched",
    //         timestamp: new Date().toISOString()
    //     };

    //     await ctx.stub.putState(txId, Buffer.from(JSON.stringify(match)));
    //     return JSON.stringify(match);
    // }

    async finalizeTrade(ctx, buyerId, sellerId, success) {


        const buyerBytes = await ctx.stub.getState(buyerId);
        const sellerBytes = await ctx.stub.getState(sellerId);

        if (!buyerBytes || !sellerBytes) {
            throw new Error("EV not found");
        }

        let buyer = JSON.parse(buyerBytes.toString());
        let seller = JSON.parse(sellerBytes.toString());


        buyer.totalTrades += 1;
        seller.totalTrades += 1;

        // Fix: handle both boolean and string
        const isSuccessful = (success === true || success === "true");
        if (isSuccessful) {
            buyer.successfulTrades += 1;
            seller.successfulTrades += 1;
        }

        const successRateBuyer = buyer.totalTrades === 0 ? 0 :
            buyer.successfulTrades / buyer.totalTrades;

        const successRateSeller = seller.totalTrades === 0 ? 0 :
            seller.successfulTrades / seller.totalTrades;

        buyer.reputation =
            0.6 * buyer.reputation +
            0.4 * successRateBuyer;

        seller.reputation =
            0.6 * seller.reputation +
            0.4 * successRateSeller;
        
        await ctx.stub.putState(buyerId, Buffer.from(JSON.stringify(buyer)));
        await ctx.stub.putState(sellerId, Buffer.from(JSON.stringify(seller)));

        return JSON.stringify({
            buyer: {
                id: buyer.id,
                reputation: buyer.reputation
            },
            seller: {
                id: seller.id,
                reputation: seller.reputation
            }
        });
    }

    async validateTransaction(ctx, validatorId, latency, isCorrect) {

        // 🔥 call your incentive logic
        return await this.updateValidatorMetrics(ctx, validatorId, latency, isCorrect);
    }

    async completeTransaction(ctx, buyerId, sellerId, success, latency, mode) {

    // ==============================
    // STEP 0: Normalize input
    // ==============================
    const isValid = (success === true || success === "true");
    const latencyVal = parseFloat(latency);
    if (!mode) mode = "proposed";

    // ==============================
    // STEP 1: Select best validator
    // ==============================
    const selectedValidator = JSON.parse(await this.selectValidator(ctx, mode));

    if (!selectedValidator) {
        throw new Error("No validator available");
    }

    // ==============================
    // STEP 2: Finalize trade
    // ==============================
    await this.finalizeTrade(ctx, buyerId, sellerId, isValid);

    // ==============================
    // STEP 3: Update validator metrics
    // ==============================
    await this.updateValidatorMetrics(
        ctx,
        selectedValidator.id,
        latencyVal,
        isValid
    );

    // ==============================
    // STEP 4: Store transaction
    // ==============================
    const txId = ctx.stub.getTxID();

    const txRecord = {
        txId,
        buyerId,
        sellerId,
        validator: selectedValidator.id,
        latency: latencyVal,
        success: isValid,
        timestamp: new Date().toISOString()
    };

    await ctx.stub.putState(txId, Buffer.from(JSON.stringify(txRecord)));

    return JSON.stringify({
        message: "Transaction completed",
        validatorUsed: selectedValidator.id
    });
}

    async getAllValidators(ctx) {

        const iterator = await ctx.stub.getStateByRange('', '');
        const results = [];

        let res = await iterator.next();
        while (!res.done) {
            const key = res.value.key;

            if (key.startsWith("VALIDATOR_")) {
                const value = res.value.value.toString('utf8');
                results.push(JSON.parse(value));
            }

            res = await iterator.next();
        }

        return JSON.stringify(results);
    }

    async resetAllValidators(ctx) {
        const iterator = await ctx.stub.getStateByRange('', '');
        let count = 0;

        let res = await iterator.next();
        while (!res.done) {
            const key = res.value.key;

            if (key.startsWith("VALIDATOR_")) {
                const val = JSON.parse(res.value.value.toString());
                val.reputation = 0;
                val.totalValidations = 0;
                val.successfulValidations = 0;
                val.successRate = 0;
                val.avgLatency = 0;
                val.lastLatency = 0;
                await ctx.stub.putState(key, Buffer.from(JSON.stringify(val)));
                count++;
            }

            res = await iterator.next();
        }

        return JSON.stringify({ message: `Reset ${count} validators` });
    }

    // async getAllPlans(ctx) {
    //     const iterator = await ctx.stub.getStateByRange('', '');
    //     const results = [];

    //     let res = await iterator.next();
    //     while (!res.done) {
    //         const value = res.value.value.toString('utf8');
    //         try {
    //             const obj = JSON.parse(value);

    //             if (obj && (obj.type === "buyer" || obj.type === "seller")) {
    //                 results.push(obj);
    //             }
    //         } catch (err) {}
    //         res = await iterator.next();
    //     }

    //     return JSON.stringify(results);
    // }

    // async matchPlans(ctx) {

    //     const iterator = await ctx.stub.getStateByRange('', '');
    //     const buyers = [];
    //     const sellers = [];
    //     const evMap = {};

    //     let res = await iterator.next();

    //     while (!res.done) {
    //         const value = res.value.value.toString('utf8');

    //         try {
    //             const obj = JSON.parse(value);

    //             if (obj.type === "buyer") buyers.push(obj);
    //             else if (obj.type === "seller") sellers.push(obj);
    //             else if (obj.id) evMap[obj.id] = obj;  // EV data

    //         } catch (err) {}

    //         res = await iterator.next();
    //     }

    //     let matches = [];

    //     for (let buyer of buyers) {
    //         for (let seller of sellers) {

    //             if (seller.price <= buyer.price && seller.energy >= buyer.energy) {
    //                 const sellerRep = evMap[seller.evId] ? evMap[seller.evId].reputation : 0;
                    
    //                 matches.push({
    //                     buyer: buyer.evId,
    //                     seller: seller.evId,
    //                     energy: buyer.energy,
    //                     price: seller.price,
    //                     sellerReputation: sellerRep
    //                 });

                    
    //             }
    //         }
    //     }

    //     matches.sort((a, b) => b.sellerReputation - a.sellerReputation);

    //     return JSON.stringify(matches);
    // }

    async queryEV(ctx, evId) {
        const evBytes = await ctx.stub.getState(evId);

        if (!evBytes) throw new Error("EV not found");

        const ev = JSON.parse(evBytes.toString());

        return JSON.stringify({
            id: ev.id,
            reputation: ev.reputation,
            totalTrades: ev.totalTrades
        });
    }
}

module.exports = V2VContract;