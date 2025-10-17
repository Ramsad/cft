# -*- coding: utf-8 -*-
from future.builtins import round
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import math
from odoo.tools import float_round


class OdSportsReceipt(models.Model):
    _name = "od.sports.receipt"
    _description = "Sports Receipt"
    _order = "id desc"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'analytic.mixin']


    name = fields.Char(string="Name", copy=False, required=True, default="/")
    date = fields.Date(string="Date", required=True)
    activities_id = fields.Many2one("od.activities", string="Program", required=True)

    move_id = fields.Many2one("account.move", string="Journal Entry", readonly=True, copy=False)
    provision_move_id = fields.Many2one("account.move", string="Commission Journal", readonly=True, copy=False)

    state = fields.Selection(
        [("draft", "Draft"), ("confirm", "Confirm"), ("cancel", "Cancel")],
        string="Status",
        default="draft",
    )

    venue_id = fields.Many2one("od.venue", string="Venue")
    venue_comm = fields.Float(string="Venue Commission")
    coach_id = fields.Many2one("res.partner", string="Coach")
    academy_id = fields.Many2one("res.partner", string="Academy", readonly=True)

    term_id = fields.Many2one("od.terms", string="Term")
    fees = fields.Float(string="Fees", readonly=True)
    no_of_class = fields.Integer(string="Number Of Class", readonly=True)

    collection_account_ids = fields.Many2many("account.account", string="Collection Accounts")
    receipt_line = fields.One2many("od.sports.receipt.line", "receipt_id", string="Receipt Lines")

    type_ids = fields.Many2one("od.camp.type")

    od_amount_total = fields.Float(string="Fees", compute="_compute_totals", store=True)
    od_grand_total = fields.Float(string="Total", compute="_compute_totals", store=True)
    od_transportation_total = fields.Float(string="Registration", compute="_compute_totals",  store=True)
    od_total_vat = fields.Float(string="VAT Total", compute="_compute_totals", store=True)

    od_commission_perc = fields.Float(string="Coach Commission %")

    @api.depends("receipt_line.transportation", "receipt_line.total", "receipt_line.amount", "receipt_line.od_vat_amount")
    def _compute_totals(self):
        for rec in self:
            rec.od_amount_total = sum(rec.receipt_line.mapped("amount"))
            rec.od_grand_total = sum(rec.receipt_line.mapped("grand_total"))
            rec.od_transportation_total = sum(rec.receipt_line.mapped("transportation"))
            rec.od_total_vat = sum(rec.receipt_line.mapped("od_vat_amount"))

    def set_to_draft(self):
        self.write({"state": "draft"})

    def unlink(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("You cannot delete this record because it is not in Draft."))
        return super().unlink()

        # helper (put near the top of the model file)
    def _analytic_dist(self,analytic):
        """Return v18 analytic_distribution for a single analytic account."""
        return {str(analytic): 100} if analytic else False

    # add these helpers in your model (e.g., on OdSportsReceipt)
    def _get_tax_account(self, tax):
        """Return the proper tax account from repartition lines (v14+)."""
        if not tax:
            return False
        # For customer-side (receipts/sales), use invoice repartition lines
        rl = tax.invoice_repartition_line_ids.filtered(
            lambda r: r.repartition_type == 'tax' and r.account_id
        )[:1]
        if rl:
            return rl.account_id.id
        # Fallback: if company runs cash-basis and only transition is set
        return tax.cash_basis_transition_account_id.id if tax.cash_basis_transition_account_id else False

    def action_confirm(self):
        self.ensure_one()
        rec = self

        if rec.move_id:
            raise UserError(_("Entry already created!"))
        if rec.provision_move_id:
            raise UserError(_("Entry already created!"))

        if rec.name == "/":
            rec.name = self.env["ir.sequence"].next_by_code("od.sports.receipt") or "/"

        # Resolve accounting configuration
        product_id = rec.term_id.product_id.id if rec.term_id and rec.term_id.product_id else False
        coach_percentage = rec.activities_id.coach_percentage
        od_cost_centre_id = rec.activities_id.cost_centre_id.id if rec.activities_id.cost_centre_id else False
        od_product_id = rec.activities_id.product_id.id if rec.activities_id.product_id else False
        academy_percentage = rec.activities_id.academy_percentage

        collection_journal = rec.activities_id.collection_journal_id
        prepaid_rev_acc = rec.activities_id.prepaid_revenue_account_id
        registration_acc = rec.activities_id.registration_acc_id
        prepaid_exp_acc = rec.activities_id.prepaid_expense_account_id
        nonrev_acc = rec.activities_id.nonrevenue_account_id
        academy_comm_exp = rec.activities_id.academy_comm_exp_id
        coach_comm_exp = rec.activities_id.coach_comm_exp_id
        account_coach_comm_collected = rec.activities_id.account_coach_comm_collected_id
        provision_journal = rec.activities_id.provision_journal_id

        if not prepaid_rev_acc:
            raise UserError(_("Define Prepaid Revenue account in Program (Activities)."))
        if not registration_acc:
            raise UserError(_("Define Registration account in Program (Activities)."))
        if not collection_journal:
            raise UserError(_("Define Collection journal in Program (Activities)."))
        if not nonrev_acc:
            raise UserError(_("Define Revenue/Non-Revenue account in Program (Activities)."))
        if not academy_comm_exp:
            raise UserError(_("Define Academy Commission Expense account in Program (Activities)."))
        if not (coach_comm_exp and account_coach_comm_collected and provision_journal):
            raise UserError(_("Set proper accounts/journal for coach commission provisions."))

        partner_payable = rec.venue_id.management_id.property_account_payable_id.id if rec.venue_id and rec.venue_id.management_id and rec.venue_id.management_id.property_account_payable_id else False
        coach_payable = rec.coach_id.property_account_payable_id.id if rec.coach_id and rec.coach_id.property_account_payable_id else False
        if not (partner_payable and coach_payable):
            raise UserError(_("Define payable accounts for venue management and coach."))

        date = rec.date

        # Ensure invoice numbers on lines (if configured)
        IrConfigParam = self.env["ir.config_parameter"].sudo()
        inv_seq_xmlid = IrConfigParam.get_param("orchid_sports_v10.receipt_inv_no", False)

        for line in rec.receipt_line:
            if line.od_invoice_no == "/" and inv_seq_xmlid:
                line.od_invoice_no = self.env["ir.sequence"].next_by_code(inv_seq_xmlid) or "/"

        # Build accounting lines
        move_lines = []
        provision_lines = []

        for line in rec.receipt_line:
            nm = line.rv_no or ""
            if line.remarks:
                nm = f"{nm} [{line.remarks}] {line.od_invoice_no or ''}"
            else:
                nm = f"{nm} {line.od_invoice_no or ''}"

            commission = line.coach_commision or 0.0
            od_cc = (line.type_id.cost_centre_id.id if (line.type_id and line.type_id.cost_centre_id) else False)

            if not rec.receipt_line:
                raise UserError(_("No receipt lines defined."))
            if not od_cc:
                raise UserError(_("Define Cost Centre on the selected Fees Type."))

            if not line.payment_type_account_id:
                raise UserError(_("Define Account on the line."))

            # Collection (Debit customer / cash/bank/clearing, depending on config)
            fee_dr = (0, 0, {
                "name": nm,
                "account_id": line.payment_type_account_id.id,
                "debit": line.grand_total,
                "credit": 0.0,
                "partner_id": line.partner_id.id if line.partner_id else False,
                "product_id": product_id,
                "analytic_distribution": self._analytic_dist(rec.venue_id.analytic_acc_id.id if rec.venue_id and rec.venue_id.analytic_acc_id else False),
                "orchid_cc_id": od_cc or False,
            })
            move_lines.append(fee_dr)

            # Non-revenue / revenue (credit)
            total_cr = (0, 0, {
                "name": nm,
                "account_id": nonrev_acc.id,
                "debit": 0.0,
                "credit": line.amount,
                "partner_id": rec.coach_id.id if rec.coach_id else False,
                "product_id": product_id,
                "analytic_distribution": self._analytic_dist(rec.venue_id.analytic_acc_id.id if rec.venue_id and rec.venue_id.analytic_acc_id else False),
                "orchid_cc_id": od_cc or False,
            })
            move_lines.append(total_cr)

            # VAT (credit)
            if line.od_vat_id:
                tax_cr = (0, 0, {
                    "name": nm,
                    "ref": rec.name,
                    "account_id": self._get_tax_account(line.od_vat_id),
                    "debit": 0.0,
                    "credit": line.od_vat_amount or 0.0,
                    "partner_id": line.partner_id.id if line.partner_id else False,
                    "product_id": product_id,
                    "analytic_distribution": self._analytic_dist(rec.venue_id.analytic_acc_id.id if rec.venue_id and rec.venue_id.analytic_acc_id else False),
                    "orchid_cc_id": od_cc or False,
                })
                move_lines.append(tax_cr)

            # Registration (credit)
            if line.transportation:
                reg_cr = (0, 0, {
                    "name": nm,
                    "account_id": registration_acc.id,
                    "debit": 0.0,
                    "credit": line.transportation or 0.0,
                    "partner_id": rec.coach_id.id if rec.coach_id else False,
                    "product_id": product_id,
                    "analytic_distribution": self._analytic_dist(rec.venue_id.analytic_acc_id.id if rec.venue_id and rec.venue_id.analytic_acc_id else False),
                    "orchid_cc_id": od_cc or False,
                })
                move_lines.append(reg_cr)

            # Provision entries (coach & venue commissions)
            # Coach Expense (DR)
            if commission:
                prov_coach_dr = (0, 0, {
                    "name": nm,
                    "account_id": coach_comm_exp.id,
                    "debit": commission,
                    "credit": 0.0,
                    "partner_id": rec.coach_id.id if rec.coach_id else False,
                    "product_id": product_id,
                    "analytic_distribution": self._analytic_dist(rec.venue_id.analytic_acc_id.id if rec.venue_id and rec.venue_id.analytic_acc_id else False),
                    "orchid_cc_id": od_cc or False,
                })
                provision_lines.append(prov_coach_dr)

                prov_coach_cr = (0, 0, {
                    "name": nm,
                    "account_id": coach_payable,
                    "debit": 0.0,
                    "credit": commission,
                    "partner_id": rec.coach_id.id if rec.coach_id else False,
                    "product_id": product_id,
                    "analytic_distribution": self._analytic_dist(rec.venue_id.analytic_acc_id.id if rec.venue_id and rec.venue_id.analytic_acc_id else False),
                    "orchid_cc_id": od_cc or False,
                })
                provision_lines.append(prov_coach_cr)

            # Venue commission provision (DR expense / CR payable to venue management)
            venue_comm_amt = (line.total * (rec.venue_comm or 0.0) / 100.0)
            if venue_comm_amt:
                prov_venue_dr = (0, 0, {
                    "name": nm,
                    "account_id": academy_comm_exp.id,
                    "debit": venue_comm_amt,
                    "credit": 0.0,
                    "partner_id": rec.venue_id.owner.id if rec.venue_id and rec.venue_id.owner else False,
                    "product_id": product_id,
                    "analytic_distribution": self._analytic_dist(rec.venue_id.analytic_acc_id.id if rec.venue_id and rec.venue_id.analytic_acc_id else False),
                    "orchid_cc_id": od_cc or False,
                })
                prov_venue_cr = (0, 0, {
                    "name": nm,
                    "account_id": partner_payable,
                    "debit": 0.0,
                    "credit": venue_comm_amt,
                    "partner_id": rec.coach_id.id if rec.coach_id else False,
                    "product_id": product_id,
                    "analytic_distribution": self._analytic_dist(rec.venue_id.analytic_acc_id.id if rec.venue_id and rec.venue_id.analytic_acc_id else False),
                    "orchid_cc_id": od_cc or False,
                })
                provision_lines += [prov_venue_dr, prov_venue_cr]

        # Create & post the main entry
        move_vals = {
            "journal_id": collection_journal.id,
            "date": date,
            "ref": rec.name,
            "line_ids": move_lines,
        }
        move = self.env["account.move"].create(move_vals)
        move.action_post()

        # Create & post the provision entry (if any)
        prov_move = False
        if provision_lines:
            prov_vals = {
                "journal_id": provision_journal.id,
                "date": date,
                "ref": rec.name,
                "line_ids": provision_lines,
            }
            prov_move = self.env["account.move"].create(prov_vals)
            prov_move.action_post()

        rec.write({"state": "confirm", "move_id": move.id, "provision_move_id": (prov_move.id if prov_move else False)})
        return True

    def action_cancel(self):
        for rec in self:
            if rec.provision_move_id:
                rec.provision_move_id.button_cancel()
                rec.provision_move_id.unlink()
            if rec.move_id:
                rec.move_id.button_cancel()
                rec.move_id.unlink()
            rec.state = "cancel"
        return True

    @api.model
    def get_round(self, value):
        return math.floor(value * 100 + 0.50) / 100

    @api.onchange("venue_id")
    def _onchange_venue_id(self):
        if self.venue_id:
            self.venue_comm = self.venue_id.commission or 0.0

    @api.onchange("od_commission_perc")
    def _onchange_commission_perc(self):
        for line in self.receipt_line:
            line.coach_commision = line.amount * (self.od_commission_perc / 100.0)

    @api.onchange("venue_comm")
    def _onchange_venue_comm(self):
        for line in self.receipt_line:
            line.od_venue_commission = line.total * (self.venue_comm / 100.0)

    @api.onchange('activities_id')
    def _onchange_activities_id(self):
        self.coach_id = self.activities_id.coach_id.id if self.activities_id.coach_id.id else False



class OdSportsReceiptLine(models.Model):
    _name = "od.sports.receipt.line"
    _description = "Sports Receipt Line"

    receipt_id = fields.Many2one("od.sports.receipt", string="Sports Receipt", ondelete="cascade")
    rv_no = fields.Char(string="RV/Number", required=True)
    partner_id = fields.Many2one("res.partner", string="Student", required=True)

    amount = fields.Float(string="Fees")
    transportation = fields.Float(string="Registration",digits=(16, 2) )

    total = fields.Float(string="Amount", compute="_compute_total", store=True)
    payment_type_account_id = fields.Many2one("account.account", string="Account", required=True)

    remarks = fields.Char(string="Cheque No")
    date = fields.Date(string="Cheque Date")
    type_id = fields.Many2one("od.camp.type", string="Type")
    no_of_clases = fields.Float(string="No Of Classes")

    coach_commision = fields.Float(string="Coach Commission Amount", compute="_compute_commission", store=True)

    od_vat_id = fields.Many2one("account.tax", string="VAT" )
    od_vat_amount = fields.Float(string="VAT Amount", compute="_compute_vat_amount", store=True,digits=(16, 2))

    grand_total = fields.Float(string="Total", compute="_compute_grand_total", store=True)

    od_invoice_no = fields.Char(string="Inv No", default="/")
    od_commission_perc = fields.Float(string="Commission %")
    od_venue_commission = fields.Float(string="Venue Commission", compute="_compute_venue_commission", store=True)

    @api.model
    def create(self, vals):
        # Auto-create registration line if student not registered for the program
        receipt = False
        if vals.get('transportation') is not None:
            vals['transportation'] = float_round(vals['transportation'], precision_digits=2)
        if vals.get("receipt_id"):
            receipt = self.env["od.sports.receipt"].browse(vals["receipt_id"])
        if receipt and vals.get("partner_id"):
            program_id = receipt.activities_id.id or False
            existing = self.env["od.registration.line"].search([("activities_id", "=", program_id),
                                                                ("partner_id", "=", vals["partner_id"])], limit=1)
            partner = self.env["res.partner"].browse(vals["partner_id"])
            if not existing:
                self.env["od.registration.line"].create({
                    "email": partner.email or "",
                    "od_dob": getattr(partner, "od_dob", False),
                    "activities_id": program_id,
                    "partner_id": vals["partner_id"],
                    "rv_no": partner.mobile or "",
                })
        return super().create(vals)

    @api.depends("transportation", "amount")
    def _compute_total(self):
        for rec in self:
            rec.total = float_round((rec.transportation or 0.0) + (rec.amount or 0.0),precision_digits=2)

    @api.onchange("amount", "type_id", "receipt_id")
    def _onchange_amount(self):
        if not self.receipt_id or not self.receipt_id.activities_id:
            return
        if not self.receipt_id.term_id:
            return
        activity_id = self.receipt_id.activities_id.id
        term_name = self.receipt_id.term_id.name
        if self.type_id:
            fee_field = "t1_fee" if term_name == "Term-1" else "t2_fee" if term_name == "Term-2" else "t3_fee"
            camp_line = self.env["od.activities.camp.line"].search(
                [("type_id", "=", self.type_id.id), ("activities_id", "=", activity_id)], limit=1)
            class_amount = getattr(camp_line, fee_field, 0.0) if camp_line else 0.0
            if class_amount:
                self.no_of_clases = float_round((self.amount or 0.0) / class_amount,precision_digits=2)

    @api.onchange("payment_type_account_id")
    def _onchange_payment_type_account_id(self):
        if self.receipt_id:
            ids = self.receipt_id.collection_account_ids.ids
            return {"domain": {"payment_type_account_id": [("id", "in", ids)]}}

    @api.onchange("type_id")
    def _onchange_type_id(self):
        if self.receipt_id and self.receipt_id.activities_id:
            ids = self.receipt_id.activities_id.camp_line.mapped("type_id").ids
            return {"domain": {"type_id": [("id", "in", ids)]}}

    @api.depends("receipt_id.od_commission_perc", "amount")
    def _compute_commission(self):
        for rec in self:
            perc = rec.receipt_id.od_commission_perc or 0.0
            rec.coach_commision = float_round((rec.amount or 0.0) * (perc / 100.0),precision_digits=2)

    @api.depends("receipt_id.venue_comm", "total")
    def _compute_venue_commission(self):
        for rec in self:
            perc = rec.receipt_id.venue_comm or 0.0
            rec.od_venue_commission = float_round((rec.total or 0.0) * (perc / 100.0),precision_digits=2)

    @api.depends("od_vat_id", "total")
    def _compute_vat_amount(self):
        for rec in self:
            tax_perc = rec.od_vat_id.amount if rec.od_vat_id else 0.0
            raw = rec.total or 0.0 * (tax_perc / 100.0)
            rec.od_vat_amount = float_round(raw, precision_digits=2, rounding_method='DOWN')

    @api.depends("total", "od_vat_amount")
    def _compute_grand_total(self):
        for rec in self:
            rec.grand_total = float_round((float_round(rec.total,2) or 0.0) + (float_round(rec.od_vat_amount,2) or 0.0),precision_digits=2)

    def od_print_invoice(self):
        self.ensure_one()
        # Replace legacy ir.actions.report.xml with modern report_action
        return self.env.ref("orchid_sports_v10.od_sports_receipt_line_pdf").report_action(self)

    @api.onchange('transportation')
    def _onchange_transportation(self):
        for rec in self:
            if rec.transportation is not None:
                rec.transportation = float_round(rec.transportation, precision_digits=2)



    def write(self, vals):
        if 'transportation' in vals and vals['transportation'] is not None:
            vals['transportation'] = float_round(vals['transportation'], precision_digits=2)
        return super().write(vals)