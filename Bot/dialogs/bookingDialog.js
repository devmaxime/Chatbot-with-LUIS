// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

const { TimexProperty } = require('@microsoft/recognizers-text-data-types-timex-expression');
const { InputHints, MessageFactory } = require('botbuilder');
const { ConfirmPrompt, TextPrompt, WaterfallDialog } = require('botbuilder-dialogs');
const { CancelAndHelpDialog } = require('./cancelAndHelpDialog');
const { DateResolverDialog } = require('./dateResolverDialog');

const CONFIRM_PROMPT = 'confirmPrompt';
const DATE_RESOLVER_DIALOG = 'dateResolverDialog';
const TEXT_PROMPT = 'textPrompt';
const WATERFALL_DIALOG = 'waterfallDialog';

class BookingDialog extends CancelAndHelpDialog {
    constructor(id, telemetryClient) {
        super(id || 'bookingDialog');

        this.addDialog(new TextPrompt(TEXT_PROMPT))
            .addDialog(new ConfirmPrompt(CONFIRM_PROMPT))
            .addDialog(new DateResolverDialog(DATE_RESOLVER_DIALOG))
            .addDialog(new WaterfallDialog(WATERFALL_DIALOG, [
                this.destinationStep.bind(this),
                this.originStep.bind(this),
                this.startDateStep.bind(this),
                this.endDateStep.bind(this),
                this.budgetStep.bind(this),
                this.confirmStep.bind(this),
                this.finalStep.bind(this)
            ]));

        this.initialDialogId = WATERFALL_DIALOG;
        this.telemetryClient = telemetryClient;
    }

    /**
     * If a destination city has not been provided, prompt for one.
     */
    async destinationStep(stepContext) {
        const bookingDetails = stepContext.options;

        if (!bookingDetails.destination) {
            const messageText = 'To what city would you like to travel?';
            const msg = MessageFactory.text(messageText, messageText, InputHints.ExpectingInput);
            return await stepContext.prompt(TEXT_PROMPT, { prompt: msg });
        }
        return await stepContext.next(bookingDetails.destination);
    }

    /**
     * If an origin city has not been provided, prompt for one.
     */
    async originStep(stepContext) {
        const bookingDetails = stepContext.options;

        // Capture the response to the previous step's prompt
        if (!bookingDetails.destination) { bookingDetails.destination = stepContext.result };
        
        if (!bookingDetails.origin) {
            const messageText = 'From what city will you be travelling?';
            const msg = MessageFactory.text(messageText, 'From what city will you be travelling?', InputHints.ExpectingInput);
            return await stepContext.prompt(TEXT_PROMPT, { prompt: msg });
        }
        return await stepContext.next(bookingDetails.origin);
    }

    /**
     * If a start date has not been provided, prompt for one.
     * This will use the DATE_RESOLVER_DIALOG.
     */
    async startDateStep(stepContext) {
        const bookingDetails = stepContext.options;

        // Capture the results of the previous step
        if (!bookingDetails.origin) { bookingDetails.origin = stepContext.result };

        if (!bookingDetails.str_date) {
            
            return await stepContext.beginDialog(DATE_RESOLVER_DIALOG, { date: bookingDetails.startDateStep, msg : 'travel'});
        }
        return await stepContext.next(bookingDetails.startDateStep);
    }

        /**
     * If a end date has not been provided, prompt for one.
     * This will use the DATE_RESOLVER_DIALOG.
     */
         async endDateStep(stepContext) {
            const bookingDetails = stepContext.options;
    
            // Capture the results of the previous step
            if (!bookingDetails.str_date) { bookingDetails.str_date = stepContext.result };

            if (!bookingDetails.end_date) {
                return await stepContext.beginDialog(DATE_RESOLVER_DIALOG, { date: bookingDetails.endDateStep, msg : 'come back'});
            }
            return await stepContext.next(bookingDetails.endDateStep);
        }

        /**
     * If an budget has not been provided, prompt for one.
     */
    async budgetStep(stepContext) {
        const bookingDetails = stepContext.options;
    
        // Capture the response to the previous step's prompt
        if (!bookingDetails.end_date) { bookingDetails.end_date = stepContext.result };

        if (!bookingDetails.budget) {
            const messageText = 'What is your budget ?';
            const msg = MessageFactory.text(messageText, messageText, InputHints.ExpectingInput);
            return await stepContext.prompt(TEXT_PROMPT, { prompt: msg });
        }
        return await stepContext.next(bookingDetails.budget);
    }

    /**
     * Confirm the information the user has provided.
     */
    async confirmStep(stepContext) {
        const bookingDetails = stepContext.options;

        // Capture the results of the previous step
        if (!bookingDetails.budget) { bookingDetails.budget = stepContext.result };

        const messageText = `Please confirm, I have you traveling to: ${ bookingDetails.destination } from: ${ bookingDetails.origin } on: ${ bookingDetails.str_date } and come back on: ${ bookingDetails.end_date }. Your budget is ${ bookingDetails.budget } Is this correct?`;
        const msg = MessageFactory.text(messageText, messageText, InputHints.ExpectingInput);

        // Offer a YES/NO prompt.
        return await stepContext.prompt(CONFIRM_PROMPT, { prompt: msg });
    }

    /**
     * Complete the interaction and end the dialog.
     */
    async finalStep(stepContext) {
        if (stepContext.result === true) {
            const bookingDetails = stepContext.options;
            return await stepContext.endDialog(bookingDetails);
        }
        else {
            this.telemetryClient.trackTrace({
                message: 'User return No during the confirmation step. See properties for more informations.',
                properties: {
                    context: stepContext.options, 

                }
            });
            console.log('Trace sent.')
        }
        return await stepContext.endDialog();
    }

    isAmbiguous(timex) {
        const timexPropery = new TimexProperty(timex);
        return !timexPropery.types.has('definite');
    }
}

module.exports.BookingDialog = BookingDialog;
