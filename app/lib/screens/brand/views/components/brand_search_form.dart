import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:modera/theme/input_decoration_theme.dart';

class BrandSearchForm extends StatelessWidget {
  const BrandSearchForm({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Form(
      child: TextFormField(
        onSaved: (newValue) {},
        validator: (value) {
          return null;
        },
        decoration: InputDecoration(
          hintText: "Find something...",
          filled: false,
          border: secodaryOutlineInputBorder(context),
          enabledBorder: secodaryOutlineInputBorder(context),
          prefixIcon: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 10),
            child: SvgPicture.asset(
              "assets/icons/Search.svg",
              height: 24,
              colorFilter: ColorFilter.mode(
                Theme.of(context).iconTheme.color!.withOpacity(0.3),
                BlendMode.srcIn,
              ),
            ),
          ),
          suffixIcon: SizedBox(
            width: 40,
            child: Row(
              children: [
                const SizedBox(
                  height: 24,
                  child: VerticalDivider(width: 1),
                ),
                Expanded(
                  child: IconButton(
                    onPressed: () {},
                    icon: SvgPicture.asset(
                      "assets/icons/Filter.svg",
                      height: 24,
                      colorFilter: ColorFilter.mode(
                        Theme.of(context).iconTheme.color!,
                        BlendMode.srcIn,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
