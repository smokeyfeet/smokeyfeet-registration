describe("signup", () => {
  beforeEach(() => {
    cy.visit("/");
    cy.get("input[type=submit]").as("submitBtn");

    // fill in the form
    cy.get('input[name="first_name"]').type("James");
    cy.get('input[name="last_name"]').type("Bond");
    cy.get('input[name="email"]').type("foo+6@bar.com");
    cy.get('input[name="email_repeat"]').type("foo+6@bar.com");
    cy.get('select[name="residing_country"]').select("Netherlands");

    cy.get('input[name="pass_type"]').first().click();
    cy.get('input[name="lunch"]').first().click();

    cy.get('input[name="agree_to_terms"]').click();
  });

  context("Signup form", () => {
    it("first name required", () => {
      cy.get('input[name="first_name"]').clear();
      cy.get("@submitBtn").click();
      cy.location("pathname").should("eq", "/");
    });

    it("last name required", () => {
      cy.get('input[name="last_name"]').clear();
      cy.get("@submitBtn").click();
      cy.location("pathname").should("eq", "/");
    });

    it.only("email should be equal to submit", () => {
      cy.get('input[name="email_repeat"]').clear().type("typo-foo+6@bar.com");
      cy.get("@submitBtn").click();
      cy.get(".alert")
        .should("exist")
        .contains("Ensure email verfication matches.");
    });

    // it("can submit a valid form", () => {
    //   cy.get("@submitBtn").click();

    //   cy.location("pathname").should("eq", "/thanks/");
    // });
  });
});
