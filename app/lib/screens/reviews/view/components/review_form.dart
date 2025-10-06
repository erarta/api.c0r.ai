import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:form_field_validator/form_field_validator.dart';
import 'package:modera/route/route_constants.dart';

import '../../../../constants.dart';

class ReviewForm extends StatelessWidget {
  const ReviewForm({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    final GlobalKey<FormState> formKey = GlobalKey<FormState>();
    return Form(
      key: formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            "Set a Title for your review",
            style: Theme.of(context).textTheme.titleSmall,
          ),
          const SizedBox(height: defaultPadding),
          TextFormField(
            onSaved: (reviewTitle) {},
            validator: (value) {
              return null;
            },
            textInputAction: TextInputAction.next,
            decoration: const InputDecoration(
              hintText: "Summarize review",
            ),
          ),
          const SizedBox(height: defaultPadding / 4),
          Text(
            "100 Character max",
            style: Theme.of(context).textTheme.labelSmall!.copyWith(
                  color: Theme.of(context).textTheme.bodyMedium!.color,
                  fontWeight: FontWeight.w500,
                ),
          ),
          const SizedBox(height: defaultPadding * 1.5),
          Text(
            "What did you like or dislike?",
            style: Theme.of(context).textTheme.titleSmall,
          ),
          const SizedBox(height: defaultPadding),
          TextFormField(
            onSaved: (review) {},
            validator: RequiredValidator(errorText: "This field is required").call,
            maxLines: 5,
            textInputAction: TextInputAction.done,
            decoration: const InputDecoration(
              hintText: "What should shoppers know befor?",
            ),
          ),
          const SizedBox(height: defaultPadding / 4),
          Text(
            "3000 Character max",
            style: Theme.of(context).textTheme.labelSmall!.copyWith(
                  color: Theme.of(context).textTheme.bodyMedium!.color,
                  fontWeight: FontWeight.w500,
                ),
          ),
          const Padding(
            padding: EdgeInsets.symmetric(vertical: defaultPadding),
            child: Divider(),
          ),
          Row(
            children: [
              Expanded(
                child: Text(
                  "Would you recommend this product?",
                  style: Theme.of(context).textTheme.titleSmall,
                ),
              ),
              const SizedBox(width: defaultPadding),
              CupertinoSwitch(
                onChanged: (value) {},
                activeColor: primaryMaterialColor.shade900,
                value: true,
              )
            ],
          ),
          Padding(
            padding: const EdgeInsets.only(
                top: defaultPadding * 1.5, bottom: defaultPadding),
            child: ElevatedButton(
              onPressed: () {
                // Validate the form field
                if (formKey.currentState!.validate()) {
                  Navigator.popAndPushNamed(context, productReviewsScreenRoute);
                }
              },
              child: const Text("Submit Review"),
            ),
          )
        ],
      ),
    );
  }
}
