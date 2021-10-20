// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

const { LuisRecognizer } = require('botbuilder-ai');
const { ConfirmPrompt } = require('botbuilder-dialogs');

class FlightBookingRecognizer {
    constructor(config, telemetryClient) {
        const luisIsConfigured = config && config.applicationId && config.endpointKey && config.endpoint;
        if (luisIsConfigured) {
            // Set the recognizer options depending on which endpoint version you want to use e.g v2 or v3.
            // More details can be found in https://docs.microsoft.com/azure/cognitive-services/luis/luis-migration-api-v3
            const recognizerOptions = {
                apiVersion: 'v3',
                telemetryClient: telemetryClient
            };

            this.recognizer = new LuisRecognizer(config, recognizerOptions);
        }
    }

    get isConfigured() {
        return (this.recognizer !== undefined);
    }

    /**
     * Returns an object with preformatted LUIS results for the bot's dialogs to consume.
     * @param {TurnContext} context
     */
    async executeLuisQuery(context) {
        return await this.recognizer.recognize(context);
    }

    getFromEntities(result) {
        let or_cityValue;
        if (result.entities.ticketBooking[0].or_city) {
            or_cityValue = result.entities.ticketBooking[0].or_city[0];
        }

        return { or_city: or_cityValue };
    }

    getToEntities(result) {
        let dst_cityValue;
        if (result.entities.ticketBooking[0].dst_city) {
            dst_cityValue = result.entities.ticketBooking[0].dst_city[0];
        }

        return { dst_city: dst_cityValue };
    }
    getStartDate(result) {
        let str_dateValue;
        if (result.entities.ticketBooking[0].str_date) {
            str_dateValue = result.entities.ticketBooking[0].str_date[0];
        }
        return { str_date: str_dateValue };
    }
    getEndDate(result) {
        let end_dateValue;
        if (result.entities.ticketBooking[0].end_date) {
            end_dateValue = result.entities.ticketBooking[0].end_date[0];
        }
 
        return { end_date: end_dateValue };
    }
    getBudget(result) {
        let budgetValue;
        if (result.entities.ticketBooking[0].budget) {
            budgetValue = result.entities.ticketBooking[0].budget[0];
        }

        return { budget: budgetValue };
    }
}

module.exports.FlightBookingRecognizer = FlightBookingRecognizer;
